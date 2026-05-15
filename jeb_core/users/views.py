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