from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, CustomUserAuthForm, CustomUserUpdateForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse
from django.template.response import TemplateResponse
from .models import User, SMSCode
from django.contrib import messages
from .decorators import verification_required
from .services import send_verification_code
from django.db import models
from django.db.models import Q
from orders.models import Order
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
            print(send_verification_code(user))
            
            messages.success(request, 'Ваш профиль был успешно зарегистрирован! Подтвердите номер телефона.')
            return redirect('users:profile')
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
                    send_verification_code(user)
                    return redirect('users:verify_phone')
            
            return render(request, 'users/register.html', {'form': form})
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form' : form})

@login_required(login_url='/users/login')
def verify_phone(request):
    # Если пользователь уже подтвержден, незачем ему тут быть
    if getattr(request.user, 'is_verified', False):
        return redirect('users:profile')

    if request.method == 'POST':
        user_code = request.POST.get('code')
        # Ищем последний код для этого юзера
        db_record = SMSCode.objects.filter(user=request.user).last()

        if db_record and db_record.code == user_code:
            # УСПЕХ: меняем флаг и сохраняем
            request.user.is_verified = True
            request.user.save()
            
            # Удаляем код, чтобы нельзя было использовать дважды
            db_record.delete()
            
            messages.success(request, 'Номер телефона успешно подтвержден!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Неверный код. Попробуйте еще раз.')

    return render(request, 'users/verify_phone.html')

@login_required
def resend_sms_view(request):
    print(send_verification_code(request.user))
    
    messages.success(request, 'Новый код был отправлен в консоль!')
    return redirect('users:verify_phone')
    
def login_view(request):
    if request.method == 'POST':
        form = CustomUserAuthForm(request=request,data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Вход')
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
    } )

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
            if request.headers.get('HX-Request'):
                return TemplateResponse(request, 'users/partials/account_details.html', {'user': updated_user})
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
            phone = ""
            if raw_phone.startswith('+'):
                phone = "+" + re.sub(r'\D', '', raw_phone)
            else:
                phone = re.sub(r'\D', '', raw_phone)
        else:
            phone = raw_phone

        user = User.objects.filter(phone_number=phone).first()
        
        if user:
            code = send_verification_code(user)
            print("\n" + "="*40)
            print(f"КОД ДЛЯ СБРОСА ПАРОЛЯ ДЛЯ ЮЗЕРА {user.phone_number}: {code}") 
            print("="*40 + "\n")
            request.session['reset_user_id'] = user.id
            messages.success(request, 'Код восстановления отправлен на ваш номер телефона.')
            return redirect('users:password_reset_confirm')
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
        
        db_record = SMSCode.objects.filter(user=user).last()

        if db_record and db_record.code == user_code:
            try:
                validate_password(new_password, user=user)
                
            except ValidationError as e:
                for error in e.messages:
                    messages.error(request, error)
                return render(request, 'users/password_reset_confirm.html', {'phone_number': user.phone_number})
            

            user.password = make_password(new_password)
            user.save()
            db_record.delete()
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
    
    code = send_verification_code(user)
    print(f"\n[ПОВТОР] КОД ДЛЯ СБРОСА ПАРОЛЯ: {code}\n") 
    
    messages.success(request, 'Новый код успешно отправлен!')
    return redirect('users:password_reset_confirm')

@login_required(login_url='/users/login')
def profile_password_reset_trigger_view(request):
    user = request.user
 
    code = send_verification_code(user)
    
    print("\n" + "=*="*15)
    print(f"ИНИЦИАЦИЯ СМЕНЫ ПАРОЛЯ ИЗ ПРОФИЛЯ ДЛЯ: {user.phone_number}")
    print(f"КОД: {code}")
    print("=*="*15 + "\n")
    
    messages.success(request, 'Код подтверждения отправлен на ваш номер телефона.')
    return redirect('users:password_reset_confirm')

@login_required
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
        
        request.session['pending_new_phone'] = phone
        
        old_phone = request.user.phone_number
        request.user.phone_number = phone
        code = send_verification_code(request.user) 
        request.user.phone_number = old_phone
        
        print("\n" + "=<>"*15)
        print(f"КОД ПОДТВЕРЖДЕНИЯ НОВОГО НОМЕРА {phone}: {code}")
        print("=<>"*15 + "\n")
        
        messages.success(request, 'Код подтверждения отправлен на новый номер телефона.')
        return redirect('users:phone_reset_confirm')

    return render(request, 'users/change_phone_request.html')

@login_required
def phone_reset_confirm(request):
    new_phone = request.session.get('pending_new_phone')
    if not new_phone:
        return redirect('main:Home_Page')
    if request.method == 'POST':
        user_code = request.POST.get('code')
        db_record = SMSCode.objects.filter(user=request.user).last()

        if db_record and db_record.code == user_code:
            user = request.user
            user.phone_number = new_phone
            user.save()
            
            db_record.delete()
            del request.session['pending_new_phone']
            messages.success(request, 'Номер телефона успешно изменен!')
            return redirect('main:Home_Page')
        else:
            messages.error(request, 'Неверный код подтверждения.')

    return render(request, 'users/change_phone_confirm.html', {'new_phone': new_phone})

@login_required
def phone_resend_sms(request):
    new_phone = request.session.get('pending_new_phone')
    if not new_phone:
        messages.error(request, 'Сессия изменения номера истекла. Начните заново.')
        return redirect('users:phone_reset_request')
    old_phone = request.user.phone_number
    request.user.phone_number = new_phone
    code = send_verification_code(request.user) 
    request.user.phone_number = old_phone
    print("\n" + "=<>"*15)
    print(f"[ПОВТОР] КОД ПОДТВЕРЖДЕНИЯ НОВОГО НОМЕРА {new_phone}: {code}")
    print("=<>"*15 + "\n")
        
    messages.success(request, 'Код подтверждения отправлен повторно на новый номер телефона.')
    return redirect('users:phone_reset_confirm')
