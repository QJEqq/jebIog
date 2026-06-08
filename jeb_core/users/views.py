from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, CustomUserAuthForm, CustomUserUpdateForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse
from django.template.response import TemplateResponse
from .models import User
from django.contrib import messages
from .decorators import verification_required
from auth.gateway import sendVerificationMessage, checkVerificationStatus
from django.db import models
from django.db.models import Q
from orders.models import Order
from repair.models import RepairRequest
from orders.services import create_cryptocloud_payment
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import re
from django.contrib.auth.hashers import make_password

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            result = sendVerificationMessage(user.phone_number)
            
            if result.get("status") == "error":
                form.add_error(None, result.get("message", "Ошибка отправки кода"))
                return render(request, 'users/register.html', {'form': form})
            
            tg_request_id = result.get("request_id")
            if tg_request_id:
                request.session['tg_request_id'] = tg_request_id
                messages.success(request, 'Ваш профиль был успешно зарегистрирован! Подтвердите номер телефона.')
            else:
                messages.error(request, 'Не удалось получить идентификатор запроса. Попробуйте позже.')
            return redirect('users:verify_phone')
        else:
            phone = request.POST.get('phone_number')
            email = request.POST.get('email')
            
            existing_user = User.objects.filter(
                (models.Q(phone_number=phone) | models.Q(email=email)), 
                is_verified=False
            ).first()

            if existing_user:
                existing_user.delete()
                
                new_form = CustomUserCreationForm(request.POST)
                if new_form.is_valid():
                    user = new_form.save()
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    result = sendVerificationMessage(user.phone_number)
                    
                    if result.get("status") == "error":
                        form.add_error(None, result.get("message", "Ошибка отправки кода"))
                        return render(request, 'users/register.html', {'form': form})
                    
                    tg_request_id = result.get("request_id")
                    if tg_request_id:
                        request.session['tg_request_id'] = tg_request_id
                    return redirect('users:verify_phone')
            
            return render(request, 'users/register.html', {'form': form})
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form' : form})

@login_required(login_url='/users/login')
def verify_phone(request):
    if getattr(request.user, 'is_verified', False):
        return redirect('users:profile')

    if request.method == 'POST':
        user_code = request.POST.get('code')
        tg_request_id = request.session.get('tg_request_id')
        if not tg_request_id:
            messages.error(request, 'Сессия проверки истекла или не существует. Запросите код повторно.')
            return render(request, 'users/verify_phone.html')
            
        is_valid = checkVerificationStatus(tg_request_id, user_code)

        if is_valid:
            request.user.is_verified = True
            request.user.save()
            
            if 'tg_request_id' in request.session:
                del request.session['tg_request_id']
            request.session.modified = True
            messages.success(request, 'Номер телефона успешно подтвержден!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Неверный код. Попробуйте еще раз.')

    return render(request, 'users/verify_phone.html')

@login_required
def resend_sms_view(request):
    result = sendVerificationMessage(request.user.phone_number)
    if result.get("status") == "error":
        messages.error(request, result.get("message", "Ошибка повторной отправки"))
    else:
        tg_request_id = result.get("request_id")
        if tg_request_id:
            request.session['tg_request_id'] = tg_request_id
            messages.success(request, 'Новый код был успешно отправлен в звонке')
        else:
            messages.error(request, 'Не удалось отправить новый код. Попробуйте позже.')
    return redirect('users:verify_phone')
    
def login_view(request):
    if request.method == 'POST':
        form = CustomUserAuthForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Вход выполнен успешно.')
            return redirect('users:profile')
    else:
        form = CustomUserAuthForm()
    return render(request, 'users/login.html', {'form' : form})

@verification_required
def profile_view(request):
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваш профиль был успешно обновлен!')
            if request.headers.get('HX-Request'):
                return HttpResponse(headers={'HX-Redirect' : reverse('users:profile')})
            return redirect('users:profile')
    else:
        form = CustomUserUpdateForm(instance=request.user)
    return TemplateResponse(request, 'users/profile.html', {
        'form' : form,
        'user' : request.user
    })

@verification_required
def account_details(request):
    user = User.objects.get(id=request.user.id)
    return TemplateResponse(request, 'users/partials/account_details.html',{
        'user' : user
    })

@verification_required
def edit_account_details(request):
    form = CustomUserUpdateForm(instance=request.user)
    return TemplateResponse(request,'users/partials/edit_account_details.html',{
        'user' : request.user,
        'form' : form
    })

@verification_required
def update_account_details(request):
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.clean()
            user.save()
            updated_user = User.objects.get(id=user.id)
            request.user = updated_user
            messages.success(request, 'Ваш профиль был успешно обновлен!')
            return TemplateResponse(request, 'users/partials/account_details.html', {'user': updated_user})
        else:
            return TemplateResponse(request, 'users/partials/edit_account_details.html', {'user': request.user, 'form': form})
    if request.headers.get('HX-Request'):
        return HttpResponse(headers={'HX-Redirect': reverse('users:profile')})
    return redirect('users:profile')

def logout_view(request):
    next_page = request.GET.get('next', reverse('main:Home_Page'))
    logout(request)
    messages.success(request, 'Выход выполнен')
    if request.headers.get('HX-Request'):
        return HttpResponse(headers={'HX-Redirect': next_page})
    return redirect(next_page)

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return TemplateResponse(request, 'users/partials/order_history.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related('items__component', 'items__computer'), 
        id=order_id, 
        user=request.user
    )
    return TemplateResponse(request, 'users/partials/order_detail.html', {'order': order})

@login_required
def repair_history(request):
    repair = RepairRequest.objects.filter(user=request.user).order_by('-created_at')
    return TemplateResponse(request,'users/partials/repair_history.html', {'repairs': repair})

@login_required
def repair_detail(request, repair_id):
    repair = get_object_or_404(RepairRequest, id=repair_id, user=request.user)
    return TemplateResponse(request,'users/partials/repair_detail.html', {'repair' : repair})

@login_required
def repay_order(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related('items__component', 'items__computer'), 
        id=order_id, 
        user=request.user
    )
    url = create_cryptocloud_payment(order)
    if url:
        return redirect(url)
    else:
        messages.error(request, "Не удалось создать ссылку на оплату. Попробуйте позже.")
        return redirect('users:profile')

def password_reset_request_view(request):
    if request.method == 'POST':
        raw_phone = request.POST.get('phone_number')
        if raw_phone:
            phone = "+" + re.sub(r'\D', '', raw_phone) if raw_phone.startswith('+') else re.sub(r'\D', '', raw_phone)
        else:
            phone = raw_phone

        user = User.objects.filter(phone_number=phone).first()
        if user:
            result = sendVerificationMessage(user.phone_number)
            if result.get("status") == "error":
                messages.error(request, result.get("message", "Ошибка отправки"))
            else:
                tg_request_id = result.get("request_id")
                if tg_request_id:
                    request.session['reset_user_id'] = user.id
                    request.session['tg_request_id'] = tg_request_id
                    messages.success(request, 'Код восстановления отправлен на ваш номер телефона в звонке.')
                    return redirect('users:password_reset_confirm')
                else:
                    messages.error(request, 'Ошибка генерации запроса на сервере')
        else:
            messages.error(request, f'Пользователь с номером {phone} не найден.')
            
    return render(request, 'users/password_reset_request.html')

def password_reset_confirm_view(request):
    if request.user.is_authenticated:
        user_id = request.user.id
    else:
        user_id = request.session.get('reset_user_id')
        
    if not user_id:
        return redirect('users:password_reset_request')
    
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user_code = request.POST.get('code')
        new_password = request.POST.get('new_password')
        
        tg_request_id = request.session.get('tg_request_id')
        if not tg_request_id:
            messages.error(request,'Сессия проверки истекла. Попробуйте заново.')
            return redirect('users:password_reset_request')
            
        is_valid = checkVerificationStatus(tg_request_id, user_code)

        if is_valid:
            try:
                validate_password(new_password, user=user)
            except ValidationError as e:
                for error in e.messages:
                    messages.error(request, error)
                return render(request, 'users/password_reset_confirm.html', {'phone_number': user.phone_number})
            
            user.password = make_password(new_password)
            user.save()
            
            if 'tg_request_id' in request.session:
                del request.session['tg_request_id']
            if 'reset_user_id' in request.session:
                del request.session['reset_user_id']
            request.session.modified = True
            
            messages.success(request, 'Пароль успешно изменен! Теперь вы можете войти.')
            return redirect('users:login')
        else:
            messages.error(request, 'Неверный код подтверждения.')

    return render(request, 'users/password_reset_confirm.html', {'phone_number': user.phone_number})

def password_reset_resend_sms_view(request):
    if request.user.is_authenticated:
        user_id = request.user.id
    else:
        user_id = request.session.get('reset_user_id')
    
    if not user_id:
        messages.error(request, 'Сессия восстановления истекла. Запросите код заново.')
        return redirect('users:password_reset_request')
    
    user = get_object_or_404(User, id=user_id)
    result = sendVerificationMessage(user.phone_number)
    if result.get("status") == "error":
        messages.error(request, result.get("message", "Ошибка отправки"))
    else:
        tg_request_id = result.get("request_id")
        if tg_request_id:
            request.session['tg_request_id'] = tg_request_id
            messages.success(request,'Новый код успешно отправлен')
        else:
            messages.error(request,'Не удалось отправить код. Попробуйте позже.')
        
    return redirect('users:password_reset_confirm')

@login_required(login_url='/users/login')
def profile_password_reset_trigger_view(request):
    user = request.user
    result = sendVerificationMessage(user.phone_number)
    if result.get("status") == "error":
        messages.error(request, result.get("message", "Ошибка отправки"))
    else:
        tg_request_id = result.get("request_id")
        if tg_request_id:
            request.session['reset_user_id'] = user.id 
            request.session['tg_request_id'] = tg_request_id
            messages.success(request, 'Код подтверждения отправлен на номер телефона звонком.')
            return redirect('users:password_reset_confirm')
        else:
            messages.error(request, 'Не удалось отправить код звонком')
            
    return redirect('users:profile')

@login_required(login_url='/users/login')
def phone_reset_request(request):
    if request.method=='POST':
        raw_phone = request.POST.get('new_phone_number')
        current_password = request.POST.get('current_password')

        if not current_password or not request.user.check_password(current_password):
            messages.error(request, 'Неверный текущий пароль.')
            return render(request, 'users/change_phone_request.html')
        
        if raw_phone:
            phone = "+" + re.sub(r'\D', '', raw_phone) if raw_phone.startswith('+') else re.sub(r'\D', '', raw_phone)
        else:
            messages.error(request, 'Введите корректный номер.')
            return render(request, 'users/change_phone_request.html')
        
        if User.objects.filter(phone_number=phone).exists():
            messages.error(request, 'Этот номер телефона уже привязан к другому аккаунту.')
            return render(request, 'users/change_phone_request.html')
            
        result = sendVerificationMessage(phone)
        if result.get("status") == "error":
            messages.error(request, result.get("message", "Ошибка шлюза"))
        else:
            tg_request_id = result.get("request_id")
            if tg_request_id:
                request.session['pending_new_phone'] = phone
                request.session['tg_phone_request_id'] = tg_request_id
                messages.success(request, 'Код подтверждения отправлен на новый номер телефона.')
                return redirect('users:phone_reset_confirm')
            else:
                messages.error(request, 'Не удалось отправить код подтверждения на указанный номер.')
                
    return render(request, 'users/change_phone_request.html')

@login_required(login_url='/users/login')
def phone_reset_confirm(request):
    tg_phone_request_id = request.session.get('tg_phone_request_id')
    new_phone = request.session.get('pending_new_phone')
    
    if not tg_phone_request_id or not new_phone:
        messages.error(request, 'Сессия изменения номера истекла или не существует.')
        return redirect('users:phone_reset_request')
        
    if request.method == 'POST':
        user_code = request.POST.get('code')
        is_valid = checkVerificationStatus(tg_phone_request_id, user_code)
        
        if is_valid:
            user = request.user
            user.phone_number = new_phone
            user.save()
            
            if 'tg_phone_request_id' in request.session:
                del request.session['tg_phone_request_id']
            if 'pending_new_phone' in request.session:
                del request.session['pending_new_phone']
            request.session.modified = True
            
            messages.success(request, 'Номер телефона успешно изменен!')
            return redirect('main:Home_Page')
        else:
            messages.error(request, 'Неверный код подтверждения ')

    return render(request, 'users/change_phone_confirm.html', {'new_phone': new_phone})

@login_required(login_url='/users/login')
def phone_resend_sms(request):
    new_phone = request.session.get('pending_new_phone')
    if not new_phone:
        messages.error(request, 'Сессия изменения номера истекла. Начните заново.')
        return redirect('users:phone_reset_request')
        
    result = sendVerificationMessage(new_phone)
    if result.get("status") == "error":
        messages.error(request, result.get("message", "Ошибка отправки"))
    else:
        tg_request_id = result.get("request_id")
        if tg_request_id:
            request.session['tg_phone_request_id'] = tg_request_id  
            messages.success(request, 'Код подтверждения отправлен повторно на новый номер телефона.')
        else:
            messages.error(request, 'Не удалось повторно отправить код.')
        
    return redirect('users:phone_reset_confirm')