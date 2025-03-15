from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db import models
from .forms import ExcelUploadForm
from .models import MainSection, Subsection, FinalSection, Lamp
import pandas as pd
import numpy as np
import os
from random import sample
from django.core.files.base import ContentFile
import requests
from urllib.parse import unquote
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def index(request):
    # Get first 2 main sections
    all_sections = list(MainSection.objects.all())
    first_sections = all_sections[:2]
    last_sections = all_sections[-2:] if len(all_sections) >= 2 else all_sections
    
    # Get products for each section
    section_products = {}
    for section in first_sections + last_sections:
        # Get products from this section and all its subsections
        products = Lamp.objects.filter(
            models.Q(section__subsection__main_section=section) |
            models.Q(subsection__main_section=section)
        )[:5]  # Get first 5 products
        section_products[section.id] = products
    
    # Get 18 random products (6 products for each column)
    random_products = list(Lamp.objects.all().order_by('?')[:18])
    
    # Split products into 3 groups of 6
    random_groups = [random_products[i:i+6] for i in range(0, len(random_products), 6)]
    
    # Add empty lists if we don't have enough products
    while len(random_groups) < 3:
        random_groups.append([])
    
    params = {
        'random_sections': first_sections,
        'last_sections': last_sections,
        'section_products': section_products,
        'random_groups': random_groups,
    }
    
    # Get cart data from session
    cart = request.session.get('cart', {})
    cart_count = sum(item['quantity'] for item in cart.values())
    cart_items = [
        {
            'id': pid,
            'name': item['name'],
            'quantity': item['quantity'],
            'price': item['price'],
            'image': item['image']
        }
        for pid, item in cart.items()
    ]
    cart_total = sum(item['price'] * item['quantity'] for item in cart.values())
    
    params.update({
        'cart_items': cart_items,
        'cart_count': cart_count,
        'cart_total': cart_total
    })
    
    # Get wishlist data from session
    wishlist = request.session.get('wishlist', {})
    wishlist_count = len(wishlist)
    wishlist_items = [
        {
            'id': pid,
            'name': item['name'],
            'price': item['price'],
            'image': item['image']
        }
        for pid, item in wishlist.items()
    ]
    
    params.update({
        'wishlist_items': wishlist_items,
        'wishlist_count': wishlist_count,
    })
    
    return render(request, 'svet_site/index.html', context=params)

def download_image(url):
    """Download image from URL and return as ContentFile"""
    if not url or str(url) == 'nan':
        return None
    try:
        if not url.startswith('http'):
            url = 'https://profilsveta.ru' + url
        
        # Decode URL to handle Russian characters
        decoded_url = unquote(url)
        response = requests.get(decoded_url)
        if (response.status_code == 200):
            return ContentFile(response.content, name=decoded_url.split('/')[-1])
    except Exception as e:
        print(f"Error downloading image {url}: {e}")
    return None

@staff_member_required
def upload_excel(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            try:
                df = pd.read_excel(excel_file)
                i = 0
                for _, row in df.iterrows():
                    i += 1
                    print(f"Processing row {i}")

                    # Handle section hierarchy
                    main_name = row['Название раздела']
                    sub_name = row['Название раздела.1']
                    final_name = row['Название раздела.2']
                    print(main_name, sub_name, final_name)

                    # Apply the same logic for empty/nan values
                    if not sub_name or str(sub_name) == 'nan':
                        sub_name = main_name
                        final_name = main_name
                    elif sub_name and (not final_name or str(final_name) == 'nan'):
                        final_name = sub_name

                    # Create or get sections
                    main_section, _ = MainSection.objects.get_or_create(name=main_name)
                    subsection, _ = Subsection.objects.get_or_create(
                        name=sub_name,
                        main_section=main_section
                    )
                    final_section, _ = FinalSection.objects.get_or_create(
                        name=final_name,
                        subsection=subsection
                    )

                    # Prepare lamp data
                    lamp_data = {
                        'section': final_section,
                        'model': row.get('Модель [PROP_2049]', ''),
                        'article': row.get('Артикул [CML2_ARTICLE]', ''),
                        'brand': row.get('Бренд (фабрика) [BRAND]', ''),
                        'collection': row.get('Серия (коллекция) [SERIA]', ''),
                        'style': row.get('Стиль [STIL]', ''),
                        'body_color': row.get('Цвет корпуса (арматуры) [COLOR_KORP]', ''),
                        'plafond_color': row.get('Цвет плафона (стекла) [COLOR_PLAT]', ''),
                        'body_material': row.get('Материал корпуса (арматуры) [MAT_KOR_AR]', ''),
                        'plafond_material': row.get('Материал плафона (стекла) [MAT_PL_ST]', ''),
                        'head_shape': row.get('Форма "головы" светильника [FORM_GOL]', ''),
                        'installation_type': row.get('Тип установки [TIP_YS]', ''),
                        'mounting_type': row.get('Тип крепления [TIP_KREP]', ''),
                        'bracket_count': row.get('Количество кронштейнов (консолей) [KOL_KRSH]'),
                        'lamp_count': row.get('Количество ламп (цоколей) [KOLL_LAMP]'),
                        'socket_type': row.get('Цоколь [COCOL]', ''),
                        'lamp_type': row.get('Тип ламп (основной) [TIP_LAMP_OS]', ''),
                        'max_power': row.get('Макс. мощность (для ламп накаливания) [MAX_LAMP_NAK]'),
                        'voltage': row.get('Напряжение, V [VOLT]'),
                        'ip_rating': row.get('Степень защиты IP [IP]', ''),
                        'weight': row.get('Вес светильника [VES]'),
                        'height': row.get('Высота светильника [H_SVET]'),
                        'width': row.get('Ширина светильника [W_SVET]'),
                        'head_diameter': row.get('Размер (диаметр) "головы" светильника [RAZMER_D]'),
                        'length': row.get('Длина светильника [D_SVET]'),
                        'depth': row.get('Глубина светильника [G_SVET]'),
                        'country': row.get('Страна производства [S_PROIZV]', ''),
                        'warranty': row.get('Гарантия [GARANT]', ''),
                        'description': row.get('Детальное описание', ''),
                        'price': row.get('Цена "Розничная цена"')
                    }

                    # Handle all possible image fields
                    image_fields = {
                        'main_image': row.get('Детальная картинка (путь)'),
                        'detail_image': row.get('Детальная картинка (путь)'),
                        'scheme_image': row.get('Схема-картинка [MORE_PHOTO2]'),
                        'lamp_image': row.get('фото ламп [MORE_PHOTO4]'),
                        'additional_image_1': row.get('Картика вторая [MORE_PHOTO]'),
                        'additional_image_2': row.get('доп фото 5 [MORE_PHOTO5]'),
                        'additional_image_3': row.get('доп фото 6 [MORE_PHOTO3]'),
                        'additional_image_4': row.get('доп фото 7 [MORE_PHOTO7]'),
                        'additional_image_5': row.get('доп фото 8 [MORE_PHOTO8]'),
                        'additional_image_6': row.get('доп фото 9 [MORE_PHOTO9]'),
                        'additional_image_7': row.get('доп фото 10 [MORE_PHOTO10]'),
                        'additional_image_8': row.get('доп фото 11 [MORE_PHOTO11]'),
                        'additional_image_9': row.get('доп фото 12 [MORE_PHOTO12]'),
                        'additional_image_10': row.get('доп фото 13 [MORE_PHOTO13]'),
                        'additional_image_11': row.get('доп фото 14 [MORE_PHOTO14]'),
                        'additional_image_12': row.get('доп фото 15 [MORE_PHOTO15]'),
                        'additional_image_13': row.get('доп фото 16 [MORE_PHOTO16]'),
                        'additional_image_14': row.get('доп фото 17 [MORE_PHOTO17]'),
                        'additional_image_15': row.get('доп фото 18 [MORE_PHOTO18]'),
                        'additional_image_16': row.get('доп фото 19 [MORE_PHOTO19]'),
                        'additional_image_17': row.get('доп фото 20 [MORE_PHOTO20]'),
                    }

                    # Download and add images to lamp_data
                    for field_name, url in image_fields.items():
                        if image_content := download_image(url):
                            lamp_data[field_name] = image_content
                    
                    if lamp_data['lamp_count'].__str__() == 'nan':
                        lamp_data['lamp_count'] = None
                    else:
                        lamp_data['lamp_count'] = int(lamp_data['lamp_count'])
                    
                    if lamp_data['max_power'].__str__() == 'nan':
                        lamp_data['max_power'] = None
                    else:
                        lamp_data['max_power'] = lamp_data['max_power'].replace('W', '').strip()
                    
                    if lamp_data['voltage'].__str__() == 'nan' or lamp_data['voltage'] == '-':
                        lamp_data['voltage'] = None
                    else:
                        lamp_data['voltage'] = lamp_data['voltage'].replace('V', '').strip()
                    
                    if lamp_data['weight'].__str__() == 'nan':
                        lamp_data['weight'] = None
                    else:
                        lamp_data['weight'] = lamp_data['weight'].replace('кг', '').strip().replace(',', '.').strip('.')
                    
                    if lamp_data['length'].__str__() == 'nan':
                        lamp_data['length'] = None
                    else:
                        lamp_data['length'] = lamp_data['length'].replace('мм', '').strip()
                    
                    if lamp_data['depth'].__str__() == 'nan':
                        lamp_data['depth'] = None
                    else:
                        lamp_data['depth'] = lamp_data['depth'].replace('мм', '').strip()
                    
                    if lamp_data['height'].__str__() == 'nan':
                        lamp_data['height'] = None
                    elif any(el for el in lamp_data['height'] if el.isalpha()):
                        lamp_data['height'] = lamp_data['height'].split('+')[0].strip().replace('мм', '').strip()
                    else:
                        lamp_data['height'] = lamp_data['height'].replace('мм', '').strip()
                    
                    if lamp_data['width'].__str__() == 'nan':
                        lamp_data['width'] = None
                    else:
                        lamp_data['width'] = lamp_data['width'].replace('мм', '').strip()
                    
                    if lamp_data['head_diameter'].__str__() == 'nan':
                        lamp_data['head_diameter'] = None
                    elif 'x' in lamp_data['head_diameter'].__str__():
                        lamp_data['head_diameter'] = lamp_data['head_diameter'].split('x')[0].strip()
                    else:
                        lamp_data['head_diameter'] = lamp_data['head_diameter'].replace('D=', '').replace('мм', '').strip()
                    
                    # Remove None values
                    lamp_data = {k: v for k, v in lamp_data.items() if v is not None}
                    
                    # Create lamp object
                    Lamp.objects.create(**lamp_data)

                messages.success(request, 'Файл успешно импортирован')
            except Exception as e:
                messages.error(request, f'Ошибка при импорте: {str(e)}')
    else:
        form = ExcelUploadForm()
    
    return render(request, 'admin/upload_excel.html', {'form': form})

def get_first_available_image(product):
    """Get the first available image from the product's image fields"""
    image_fields = ['main_image', 'detail_image', 'scheme_image', 'lamp_image', 
                   'additional_image_1', 'additional_image_2', 'additional_image_3']
    
    for field in image_fields:
        image = getattr(product, field, None)
        if image:
            return image
    return None

@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    if not product_id:
        return JsonResponse({'error': 'Lamp ID is required'}, status=400)
    
    try:
        product = Lamp.objects.get(id=product_id)
    except Lamp.DoesNotExist:
        return JsonResponse({'error': 'Lamp not found'}, status=404)
    
    # Initialize cart in session if it doesn't exist
    if 'cart' not in request.session:
        request.session['cart'] = {}
    
    cart = request.session['cart']
    
    # Add or increment product in cart
    if product_id in cart:
        cart[product_id]['quantity'] += 1
    else:
        cart[product_id] = {
            'quantity': 1,
            'name': product.model,
            'price': float(product.price),
            'image': get_first_available_image(product).url if get_first_available_image(product) else '',
        }
    
    request.session.modified = True
    
    # Prepare response data
    cart_items = [
        {
            'id': pid,
            'name': item['name'],
            'quantity': item['quantity'],
            'price': item['price'],
            'image': item['image']
        }
        for pid, item in cart.items()
    ]
    
    return JsonResponse({
        'status': 'success',
        'cart_count': sum(item['quantity'] for item in cart.values()),
        'cart_items': cart_items
    })

@require_POST
def add_to_wishlist(request):
    product_id = request.POST.get('product_id')
    if not product_id:
        return JsonResponse({'error': 'Product ID is required'}, status=400)
    
    try:
        product = Lamp.objects.get(id=product_id)
    except Lamp.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    
    # Initialize wishlist in session if it doesn't exist
    if 'wishlist' not in request.session:
        request.session['wishlist'] = {}
    
    wishlist = request.session['wishlist']
    
    # Add product to wishlist if not already there
    if product_id not in wishlist:
        wishlist[product_id] = {
            'name': product.model,
            'price': float(product.price),
            'image': get_first_available_image(product).url if get_first_available_image(product) else '',
        }
        request.session.modified = True
    
    return JsonResponse({
        'status': 'success',
        'wishlist_count': len(wishlist),
        'wishlist_items': [
            {
                'id': pid,
                'name': item['name'],
                'price': item['price'],
                'image': item['image']
            }
            for pid, item in wishlist.items()
        ]
    })

def lamps(request):
    # Get selected main category
    selected_main = request.GET.get('main_cat', '')
    
    # Get all lamps
    lamp_list = Lamp.objects.all()
    
    # Initialize section hierarchy with only main sections
    section_hierarchy = []
    main_sections = MainSection.objects.all()
    
    for main in main_sections:
        main_count = Lamp.objects.filter(section__subsection__main_section=main).count()
        section_hierarchy.append({
            'section': main,
            'count': main_count,
            'is_selected': str(main.id) == selected_main
        })
    
    # Apply main category filter if selected
    if selected_main:
        lamp_list = lamp_list.filter(section__subsection__main_section__id=selected_main)
        try:
            main_section = MainSection.objects.get(id=selected_main)
            breadcrumb = [('main', main_section)]
        except MainSection.DoesNotExist:
            breadcrumb = []
    else:
        breadcrumb = []

    # Get sorting parameter
    sort = request.GET.get('sort', '0')
    if sort == '1':
        lamp_list = lamp_list.order_by('price')
    elif sort == '2':
        lamp_list = lamp_list.order_by('-price')
    
    # Get items per page from request, default to 9
    per_page = request.GET.get('show', '9')
    per_page = int(per_page) if per_page in ['9', '18'] else 9
    
    # Create paginator object
    paginator = Paginator(lamp_list, per_page)
    
    # Get page number from request
    page = request.GET.get('page', 1)
    
    try:
        lamps = paginator.page(page)
    except PageNotAnInteger:
        lamps = paginator.page(1)
    except EmptyPage:
        lamps = paginator.page(paginator.num_pages)
    
    # Calculate the range of pages to show
    page_range = get_page_range(paginator, lamps.number)
    
    # Get cart data from session
    cart = request.session.get('cart', {})
    cart_count = sum(item['quantity'] for item in cart.values())
    cart_items = [
        {
            'id': pid,
            'name': item['name'],
            'quantity': item['quantity'],
            'price': item['price'],
            'image': item['image']
        }
        for pid, item in cart.items()
    ]
    cart_total = sum(item['price'] * item['quantity'] for item in cart.values())
    
    # Get wishlist data from session
    wishlist = request.session.get('wishlist', {})
    wishlist_count = len(wishlist)
    wishlist_items = [
        {
            'id': pid,
            'name': item['name'],
            'price': item['price'],
            'image': item['image']
        }
        for pid, item in wishlist.items()
    ]
    
    context = {
        'lamps': lamps,
        'page_range': page_range,
        'current_show': per_page,
        'current_sort': sort,  # Add current sort to context
        'cart_items': cart_items,
        'cart_count': cart_count,
        'cart_total': cart_total,
        'wishlist_items': wishlist_items,
        'wishlist_count': wishlist_count,
    }
    
    context.update({
        'section_hierarchy': section_hierarchy,
        'selected_main': selected_main,
        'breadcrumb': breadcrumb,
    })
    
    return render(request, 'svet_site/lamps.html', context)

def get_page_range(paginator, current_page, show_range=2):
    """
    Returns a list of page numbers to show, with ellipsis where needed.
    Example: [1, 2, 3, '...', 98, 99, 100] for current_page=2
    """
    total_pages = paginator.num_pages
    
    # Always show first and last page
    page_range = []
    
    # Calculate range around current page
    start_range = max(current_page - show_range, 1)
    end_range = min(current_page + show_range, total_pages)
    
    # Add first pages
    if start_range > 1:
        page_range.extend([1])
        if start_range > 2:
            page_range.append('...')
    
    # Add middle range
    page_range.extend(range(start_range, end_range + 1))
    
    # Add last pages
    if end_range < total_pages:
        if end_range < total_pages - 1:
            page_range.append('...')
        page_range.append(total_pages)
    
    return page_range
