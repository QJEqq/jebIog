import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.db import transaction  
from django.http import HttpResponse , HttpResponseForbidden 
from django.conf import settings  
from .services import create_cryptocloud_payment
from django.views.generic import TemplateView
from cart.views import CartMixin
from .forms import OrderForm
from .models import OrderItem, Order
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import json
import ipaddress
from django.conf import settings

from ipware import get_client_ip

logger = logging.getLogger(__name__)

class PaymentCheckView(View):
    def get(self, request):
        order_id = request.GET.get('order_id')
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if request.headers.get('HX-Request'):
            if order.status == 'paid':
                response = HttpResponse()
                response['HX-Redirect'] = '/orders/payment/success/'
                return response
            elif order.status == 'cancelled':
                response = HttpResponse()
                response['HX-Redirect'] = '/orders/payment/failed/'
                return response
            return HttpResponse(status=200)
        return render(request, 'orders/payment_check.html', {'order' : order})

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
                    raise Exception("Не удалось получить ссылку от юКасса")

            except Exception as e:
                print(f"Ошибка в POST оформления заказа: {e}") 
                messages.error(request, f"Произошла ошибка: {e}")
                if 'order' in locals():
                    order.delete()
                messages.error(request, f"Ошибка при формировании оплаты")
                return redirect('orders:checkout')

        return render(request, 'orders/checkout.html', {'form': form, 'cart': cart})


        

class PaymentSuccessView(TemplateView):
    template_name = 'orders/payment_success.html'

class PaymentFailedView(TemplateView):
    template_name = 'orders/payment_failed.html'

def check_ip_in_ranges(ip, ranges):
    try:
        client_obj = ipaddress.ip_address(ip)
        for r in ranges:
            if client_obj in ipaddress.ip_network(r):
                return True
    except ValueError:
        pass
    return False

@csrf_exempt
def yookassa_webhook(request):
    """
    Асинхронный обработчик от ЮKassa. 
    """
    if request.method != 'POST':
        return HttpResponse("Method not allowed", status=405)

    client_ip, is_routable = get_client_ip(request)
    
    if not settings.DEBUG:
        if not client_ip or not check_ip_in_ranges(client_ip, settings.YOOKASSA_IP_RANGES):
            return HttpResponseForbidden("Forbidden: Fake Webhook Attempt Detected")
        
    if not client_ip or not check_ip_in_ranges(client_ip, settings.YOOKASSA_IP_RANGES):
        return HttpResponseForbidden("Forbidden: Fake Webhook Attempt Detected")

    try:
        event_data = json.loads(request.body)
    except ValueError:
        return HttpResponse("Invalid JSON", status=400)

    payment_object = event_data.get('object', {})
    payment_id = payment_object.get('id')
    event_type = event_data.get('event')

    try:
        order = Order.objects.get(yookassa_payment_id=payment_id)
    except Order.DoesNotExist:
        return HttpResponse("Order not found, skipping", status=200)


    if event_type == 'payment.succeeded':

        if order.status == 'pending':
            order.status = 'paid' 
            order.save()
            
            
            
    elif event_type == 'payment.canceled':
        if order.status == 'pending':
            order.status = 'cancelled' 
            order.save()

    return HttpResponse("OK", status=200)