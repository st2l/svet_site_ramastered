from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def discount_percent(current_price, old_price):
    if not current_price or not old_price:
        return 0
    discount = ((float(old_price) - float(current_price)) / float(old_price)) * 100
    return int(discount)