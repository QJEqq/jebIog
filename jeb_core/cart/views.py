from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse # Добавь этот импорт
from .cart import Cart
def cart_count(request):
    cart = Cart(request)
    # Возвращаем просто число как текст
    return HttpResponse(len(cart))

def cart_add(request, item_type, product_id):
    cart = Cart(request)
    model_class = cart.VALID_ITEM_TYPES.get(item_type)
    
    if not model_class:
        return redirect('main:Home_Page')
    
    item = get_object_or_404(model_class, id=product_id)
    
    action = request.GET.get('action')
    if action == 'remove':
        cart.add(item=item, item_type=item_type, quantity=-1)
    else:
        cart.add(item=item, item_type=item_type, quantity=1)

    if request.headers.get('HX-Request'):
        # Сохраняем результат рендера в переменную
        response = render(request, 'cart/includes/item_control.html', {
            'item': item,
            'item_type': item_type,
            'cart': cart
        })
        
        # Добавляем сигнал для HTMX
        response['HX-Trigger'] = 'cartUpdated' 
        return response

    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/cart_drawer.html', {
        'cart': cart
    })