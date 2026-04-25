from django import template

register = template.Library()

@register.filter
def call_with_args(obj, args_string):
    # args_string придет как "computers,5"
    if not args_string:
        return obj()
    
    arg_list = str(args_string).split(',')
    return obj(*arg_list)

@register.simple_tag
def get_cart_qty(cart, item_type, item_id):
    # Если cart пришел как строка или None (значит во вьюхе его забыли)
    if isinstance(cart, str) or cart is None:
        return 0
    
    # Пытаемся вызвать метод, если он есть
    try:
        return cart.get_item_quantity(item_type, item_id)
    except AttributeError:
        return 0