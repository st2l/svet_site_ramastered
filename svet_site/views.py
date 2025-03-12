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

def index(request):
    # Get first 2 main sections
    all_sections = list(MainSection.objects.all())
    first_sections = all_sections[:2]
    
    # Get products for each section
    section_products = {}
    for section in first_sections:
        # Get products from this section and all its subsections
        products = Lamp.objects.filter(
            models.Q(section__subsection__main_section=section) |
            models.Q(subsection__main_section=section)
        )[:5]  # Get first 5 products
        section_products[section.id] = products
    
    params = {
        'random_sections': first_sections,  # Keeping the same parameter name for template compatibility
        'section_products': section_products,
    }
    
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
        if response.status_code == 200:
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
