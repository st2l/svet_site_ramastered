from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .forms import ExcelUploadForm
from .models import MainSection, Subsection, FinalSection, Lamp
import pandas as pd
import numpy as np
import os

def index(request):
    return render(request, 'svet_site/index.html')

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

                    # Handle image fields
                    if str(row.get('Детальная картинка (путь)')) != 'nan':
                        lamp_data['main_image'] = row['Детальная картинка (путь)']
                    if str(row.get('Схема-картинка [MORE_PHOTO2]')) != 'nan':
                        lamp_data['scheme_image'] = row['Схема-картинка [MORE_PHOTO2]']
                    if str(row.get('фото ламп [MORE_PHOTO4]')) != 'nan':
                        lamp_data['lamp_image'] = row['фото ламп [MORE_PHOTO4]']

                    from pprint import pprint
                    print(lamp_data['length'], type(lamp_data['length']))
                    
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
