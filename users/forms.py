import re

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm

from .models import User


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')

    class Meta:
        model = User
        fields = ['name', 'surname', 'email', 'password']


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            user = authenticate(username=email, password=password)

            if user is None:
                raise forms.ValidationError('Неверный имейл или пароль')

            self.user = user

        return cleaned_data


class EditProfileForm(forms.ModelForm):
    avatar = forms.ImageField(
        label='Аватар',
        widget=forms.FileInput(attrs={'class': 'avatar-input', 'style': 'display: none;'}),
        required=False
    )

    class Meta:
        model = User
        fields = ['name', 'surname', 'avatar', 'about', 'phone', 'github_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'surname': forms.TextInput(attrs={'class': 'form-control'}),
            'about': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')

        if not phone:
            return None

        digits = re.sub(r'\D', '', phone)
        if len(digits) == 11 and digits[0] == '8':
            digits = '7' + digits[1:]
        normalized_phone = '+' + digits

        if not re.match(r'^\+7\d{10}$', normalized_phone):
            raise forms.ValidationError(
                'Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX'
            )

        return normalized_phone

    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        if url and 'github.com' not in url:
            raise forms.ValidationError('Ссылка должна вести на GitHub')
        return url


class PasswordChangeUserForm(PasswordChangeForm):
    pass
