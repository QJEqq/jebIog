import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.db import transaction  
from django.http import HttpResponse  
from django.conf import settings  
from .services import create_cryptocloud_payment

from cart.views import CartMixin
from .forms import OrderForm
from .models import OrderItem, Order

logger = logging.getLogger(__name__)

@method_decorator(login_required(login_url='/user/login'), name='dispatch')
class CheckOutView(CartMixin, View):
    def get(self, request):
        cart = self.get_cart(request)

        if len(cart) == 0:
            messages.error(request, 'В корзине пусто. Добавьте сначала товар!')
            if request.headers.get('HX-Request'):
                return render(request, 'cart/cart.drawer.html')
            return redirect('cart:cart_detail')
        
        total_price = cart.get_total_price()
        form = OrderForm(user=request.user)

        context = {
            'form' : form,
            'cart' : cart,
            'total_price' : total_price 
        }

        if request.headers.get('HX-Request'):
            return render(request, 'orders/checkout_content.html', context)
        return render(request, 'orders/checkout.html', context)
    
    def post(self, request):
        cart = self.get_cart(request)

        if len(cart) == 0:
            messages.error(request, 'В корзине пусто. Добавьте сначала товар!')
            if request.headers.get('HX-Request'):
                return render(request, 'cart/cart.drawer.html')
            return redirect('cart:cart_detail')
        
        form = OrderForm(data=request.POST, user=request.user)
        if form.is_valid():
            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    order.user = request.user
                    order.total_price = cart.get_total_price()
                    order.save()

                    # Сохраняем товары
                    for item in cart:
                        OrderItem.objects.create(
                            order=order,
                            component=item if item.item_type == 'component' else None,
                            computer=item if item.item_type == 'computer' else None,
                            price=item.price,
                            quantity=item.quantity
                        )

                # 3. ЛОГИКА ПЛАТЕЖКИ (Интегрируем CryptoCloud)
                payment_url = create_cryptocloud_payment(order) # Наша функция-сервис
                
                if payment_url:
                    cart.clear()
                    # Если работаем через HTMX
                    if request.headers.get('HX-Request'):
                        response = HttpResponse(status=200)
                        response['HX-Redirect'] = payment_url
                        return response
                    return redirect(payment_url)
                else:
                    raise Exception("Не удалось получить ссылку от CryptoCloud")

            except Exception as e:
                print(f"Ошибка в POST: {e}") 
                messages.error(request, f"Произошла ошибка: {e}")
                if 'order' in locals():
                    order.delete()
                messages.error(request, f"Ошибка оплаты: {e}")
                return redirect('orders:checkout')

        return render(request, 'orders/checkout.html', {'form': form, 'cart': cart})


        

