from django.db import models
from django.db.models import ImageField
from django.core.exceptions import ValidationError

UPLOAD_DIR = 'upload_dir'

class MainSection(models.Model):
    name = models.CharField('Название', max_length=255)
    
    def __str__(self):
        return self.name


class Subsection(models.Model):
    name = models.CharField('Название', max_length=255)
    main_section = models.ForeignKey(MainSection, on_delete=models.CASCADE, verbose_name='Основной раздел')
    
    def __str__(self):
        return f"{self.main_section} - {self.name}"


class FinalSection(models.Model):
    name = models.CharField('Название', max_length=255)
    subsection = models.ForeignKey(Subsection, on_delete=models.CASCADE, verbose_name='Подраздел')
    
    def __str__(self):
        return f"{self.subsection} - {self.name}"


class Lamp(models.Model):
    section = models.ForeignKey(FinalSection, on_delete=models.CASCADE, verbose_name='Раздел', null=True, blank=True)
    subsection = models.ForeignKey(Subsection, on_delete=models.CASCADE, verbose_name='Подраздел', null=True, blank=True)
    
    def clean(self):
        if not self.section and not self.subsection:
            raise ValidationError('Необходимо указать либо раздел, либо подраздел')
        if self.section and self.subsection:
            raise ValidationError('Нельзя одновременно указать и раздел, и подраздел')

    # Basic identification
    model = models.CharField('Модель', max_length=255)
    article = models.CharField('Артикул', max_length=100, blank=True)
    brand = models.CharField('Бренд', max_length=100)
    
    # Classification
    collection = models.CharField('Серия (коллекция)', max_length=100, blank=True)
    style = models.CharField('Стиль', max_length=100, blank=True)
    
    # Physical properties
    body_color = models.CharField('Цвет корпуса', max_length=100, blank=True)
    plafond_color = models.CharField('Цвет плафона', max_length=100, blank=True)
    body_material = models.CharField('Материал корпуса', max_length=255, blank=True)
    plafond_material = models.CharField('Материал плафона', max_length=255, blank=True)
    head_shape = models.CharField('Форма головы', max_length=100, blank=True)
    
    # Installation details
    installation_type = models.CharField('Тип установки', max_length=100, blank=True)
    mounting_type = models.CharField('Тип крепления', max_length=255, blank=True)
    bracket_count = models.CharField('Количество кронштейнов', max_length=200, null=True, blank=True)
    
    # Technical specifications
    lamp_count = models.IntegerField('Количество ламп', null=True, blank=True)
    socket_type = models.CharField('Цоколь', max_length=50, blank=True)
    lamp_type = models.CharField('Тип ламп', max_length=100, blank=True)
    max_power = models.CharField('Макс. мощность', max_length=200, null=True, blank=True)
    voltage = models.IntegerField('Напряжение', null=True, blank=True)
    ip_rating = models.CharField('Степень защиты IP', max_length=20, blank=True)
    
    # Dimensions
    weight = models.DecimalField('Вес', max_digits=10, decimal_places=2, null=True, blank=True)
    height = models.IntegerField('Высота', null=True, blank=True)
    width = models.IntegerField('Ширина', null=True, blank=True)
    head_diameter = models.IntegerField('Размер головы', null=True, blank=True)
    length = models.IntegerField('Длина', null=True, blank=True)
    depth = models.IntegerField('Глубина', null=True, blank=True)
    
    # Additional information
    country = models.CharField('Страна производства', max_length=100, blank=True)
    warranty = models.CharField('Гарантия', max_length=100, blank=True)
    equipment = models.TextField('Комплектация', blank=True)
    description = models.TextField('Описание', blank=True)
    
    last_price = models.DecimalField('Прошлая цена', max_digits=10, decimal_places=2, null=True, blank=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Images
    main_image = models.ImageField('Основное изображение', upload_to=UPLOAD_DIR, blank=True)
    detail_image = models.ImageField('Детальная картинка', upload_to=UPLOAD_DIR, blank=True)
    scheme_image = models.ImageField('Схема', upload_to=UPLOAD_DIR, blank=True)
    lamp_image = models.ImageField('Фото ламп', upload_to=UPLOAD_DIR, blank=True)
    additional_image_1 = models.ImageField('Картинка вторая', upload_to=UPLOAD_DIR, blank=True)
    additional_image_2 = models.ImageField('Доп фото 5', upload_to=UPLOAD_DIR, blank=True)
    additional_image_3 = models.ImageField('Доп фото 6', upload_to=UPLOAD_DIR, blank=True)
    additional_image_4 = models.ImageField('Доп фото 7', upload_to=UPLOAD_DIR, blank=True)
    additional_image_5 = models.ImageField('Доп фото 8', upload_to=UPLOAD_DIR, blank=True)
    additional_image_6 = models.ImageField('Доп фото 9', upload_to=UPLOAD_DIR, blank=True)
    additional_image_7 = models.ImageField('Доп фото 10', upload_to=UPLOAD_DIR, blank=True)
    additional_image_8 = models.ImageField('Доп фото 11', upload_to=UPLOAD_DIR, blank=True)
    additional_image_9 = models.ImageField('Доп фото 12', upload_to=UPLOAD_DIR, blank=True)
    additional_image_10 = models.ImageField('Доп фото 13', upload_to=UPLOAD_DIR, blank=True)
    additional_image_11 = models.ImageField('Доп фото 14', upload_to=UPLOAD_DIR, blank=True)
    additional_image_12 = models.ImageField('Доп фото 15', upload_to=UPLOAD_DIR, blank=True)
    additional_image_13 = models.ImageField('Доп фото 16', upload_to=UPLOAD_DIR, blank=True)
    additional_image_14 = models.ImageField('Доп фото 17', upload_to=UPLOAD_DIR, blank=True)
    additional_image_15 = models.ImageField('Доп фото 18', upload_to=UPLOAD_DIR, blank=True)
    additional_image_16 = models.ImageField('Доп фото 19', upload_to=UPLOAD_DIR, blank=True)
    additional_image_17 = models.ImageField('Доп фото 20', upload_to=UPLOAD_DIR, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.model
