from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, CustomUserAuthForm, CustomUserUpdateForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse
from django.template.response import TemplateResponse
from .models import User

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('main:Home_Page')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form' : form})
    
def login_view(request):
    if request.method == 'POST':
        form = CustomUserAuthForm(request=request,data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('main:Home_Page')
    else:
        form = CustomUserAuthForm()
    return render(request, 'users/login.html', {'form' : form})

@login_required(login_url='/users/login')
def profile_view(request):
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            if request.headers.get('HX-Request'):
                return HttpResponse(headers={'HX-Redirect' : reverse('users:profile')})
            return redirect('users:profile')
    else:
        form = CustomUserUpdateForm(instance=request.user)
    return TemplateResponse(request, 'users/profile.html', {
        'form' : form,
        'user' : request.user
    })

@login_required(login_url='/users/login')
def account_details(request):
    user = User.objects.get(id=request.user.id)
    return TemplateResponse(request, 'users/partials/account_details.html',{
        'user' : user
    })

@login_required(login_url='/users/login')
def edit_account_details(request):
    form = CustomUserUpdateForm(instance=request.user)
    return TemplateResponse(request,'users/partials/edit_account_details.html',{
        'user' : request.user,
        'form' : form
    } )

@login_required(login_url='/users/login')
def update_account_details(request):
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.clean()
            user.save()
            updated_user = User.objects.get(id=user.id)
            request.user = updated_user
            if request.headers.get('HX-Request'):
                return TemplateResponse(request, 'users/partials/account_details.html', {'user': updated_user})
            return TemplateResponse(request, 'users/partials/account_details.html', {'user': updated_user})
        else:
            return TemplateResponse(request, 'users/partials/edit_account_details.html', {'user': request.user, 'form': form})
    if request.headers.get('HX-Request'):
        return HttpResponse(headers={'HX-Redirect': reverse('users:profile')})
    return redirect('users:profile')


def logout_view(request):
    logout(request)
    if request.headers.get('HX-Request'):
        return HttpResponse(headers={'HX-Redirect': reverse('main:Home_Page')})
    return redirect('main:Home_Page')