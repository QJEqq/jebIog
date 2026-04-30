from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model , authenticate
from django.utils.html import strip_tags
from django.core.validators import RegexValidator
from phonenumber_field.formfields import PhoneNumberField

User = get_user_model()

COMMON_ATTRS = {
    'class' : 'dotted-input'
}

class CustomUserCreationForm(UserCreationForm):
    phone_number = PhoneNumberField(
        required=True,
        region='RU',
        widget=forms.TextInput(attrs={**COMMON_ATTRS, 'placeholder' : 'Номер телефона'})

    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={**COMMON_ATTRS, 'placeholder' : 'Почта'})
    )

    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={**COMMON_ATTRS, 'placeholder' : 'Ваше Имя'})
    )
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={**COMMON_ATTRS, 'placeholder' : 'Придумайте пароль'})
    )

    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={**COMMON_ATTRS, 'placeholder' : 'Повторите пароль'})
    )

    class Meta(UserCreationForm._meta):
        model = User
        fields = ('phone_number', 'email', 'first_name')

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if User.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError('Данный номер уже занят!')
        return phone
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit: 
            user.save()
        return user
    
class CustomUserAuthForm(AuthenticationForm):
    username = forms.CharField(
        label = 'Номер телефона',
        widget=forms.TextInput(attrs={**COMMON_ATTRS, 'placeholder' : 'Номер телефона'})

    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={**COMMON_ATTRS, 'placeholder' : 'Придумайте пароль'})
    )
