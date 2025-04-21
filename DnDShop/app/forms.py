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

class PoolForm(forms.Form):
     rating_overall = forms.IntegerField(label='Общее впечатление (1-5)', min_value=1, max_value=5)
     rating_design = forms.IntegerField(label='Внешний вид (1-5)', min_value=1, max_value=5)
     rating_content = forms.IntegerField(label='Новости и контент (1-5)', min_value=1, max_value=5)
     features_liked = forms.CharField(label='Что Вам больше всего понравилось?', widget=forms.Textarea)
     features_improve = forms.CharField(label='Что мы могли бы улучшить?', widget=forms.Textarea)
     newsletter = forms.BooleanField(label='Хотите получать бесплатную рассылку новостей?', required=False)
     contact_method = forms.ChoiceField(label='Выберите способ связи:', choices=[('email', 'Email'), ('phone', 'Телефон')])

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