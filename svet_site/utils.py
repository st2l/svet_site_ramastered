import pandas as pd

def create_example_excel():
    data = {
        'main_section': ['Потолочные светильники', 'Настенные светильники'],
        'subsection': ['Люстры', 'Бра'],
        'final_section': ['Хрустальные люстры', 'Современные бра'],
        'model': ['Crystal Light 500', 'Modern Wall 200'],
        'article': ['CL-500', 'MW-200'],
        'brand': ['LightMaster', 'WallPro'],
        'collection': ['Crystal Series', 'Modern Collection'],
        'style': ['Классический', 'Современный'],
        'body_color': ['Золото', 'Хром'],
        'plafond_color': ['Прозрачный', 'Белый'],
        'body_material': ['Металл', 'Алюминий'],
        'plafond_material': ['Хрусталь', 'Стекло'],
        'head_shape': ['Круглая', 'Квадратная'],
        'installation_type': ['Потолочный', 'Настенный'],
        'mounting_type': ['На планку', 'На кронштейн'],
        'bracket_count': [4, 2],
        'lamp_count': [5, 1],
        'socket_type': ['E27', 'E14'],
        'lamp_type': ['LED', 'LED'],
        'max_power': [60, 40],
        'voltage': [220, 220],
        'ip_rating': ['IP20', 'IP44'],
        'weight': [5.5, 1.2],
        'height': [500, 250],
        'width': [500, 150],
        'head_diameter': [400, 100],
        'length': [500, 200],
        'depth': [500, 150],
        'country': ['Италия', 'Германия'],
        'warranty': ['2 года', '1 год'],
        'equipment': ['Лампы в комплекте', 'Без ламп'],
        'description': ['Роскошная хрустальная люстра...', 'Современное настенное бра...'],
        'last_price': [15000, 5000],
        'price': [12000, 4500]
    }
    
    df = pd.DataFrame(data)
    df.to_excel('example_lamps.xlsx', index=False)
    return 'example_lamps.xlsx'

if __name__ == '__main__':
    create_example_excel()
