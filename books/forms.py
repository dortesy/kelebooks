from django import forms
from django.forms import ClearableFileInput
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from hcaptcha_field import hCaptchaField

class GetBooksForm(forms.Form):
    files = forms.FileField(widget=ClearableFileInput(attrs={'multiple': True}))
    
class ContactForm(forms.Form):
    CHOICES = [
        ('Жалоба на авторские права', 'Жалоба на авторские права'),
        ('Рекламное сотрудничество', 'Рекламное сотрудничество'),
        ('Другое', 'Другое')
    ]
    your_name = forms.CharField(label='Ваше имя', max_length=150, required=False)
    email = forms.EmailField(label='E-mail', required=False)
    subject = forms.ChoiceField(label="Тема письма", choices=CHOICES)
    message = forms.CharField(label="Сообщение", widget=forms.Textarea)
    hcaptcha = hCaptchaField(label="Капча")
    
    
    

