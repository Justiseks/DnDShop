"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Comment
from django.utils.translation import gettext_lazy as _
from .models import Blog

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'Имя'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Пароль'}))

class CommentForm(forms.ModelForm):
     class Meta:
         model = Comment
         fields = ("text", )
         labels = {"text": "Комментарий"}

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ('title', 'description', 'content', 'image')
        labels = {'title' : "Заголовок", 'description' : "Краткое содержание", 'content' : "Полное содержание", 'image' : "Картинка"}