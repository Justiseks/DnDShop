"""
Definition of models.
"""

from django.db import models
from django.contrib import admin
from datetime import datetime
from django.urls import reverse
from django.contrib.auth.models import User


# Create your models here.

class Blog(models.Model):
    title = models.CharField(max_length=100, unique_for_date="posted", verbose_name="Заголовок")
    description = models.TextField(verbose_name="Краткое содержание")
    content = models.TextField(verbose_name="Полное содержание")
    posted = models.DateTimeField(default=datetime.now, db_index=True, verbose_name="Опубликована")
    author = models.ForeignKey(User, null=True, blank=True, on_delete = models.SET_NULL, verbose_name = "Автор")
    image = models.FileField(default = 'temp.jpg', verbose_name = "Путь к картинке") 

    def get_absolute_url(self):
        return reverse("blogpost", args=[str(self.id)])
    
    def __str__(self):
        return self.title
    
    class Meta:
        db_table = "Posts"
        ordering = ["-posted"]
        verbose_name = "статья блога"
        verbose_name_plural = "статьи блога"

admin.site.register(Blog)

class Comment(models.Model):
      text = models.TextField(verbose_name="Текст комментария")
      date = models.DateTimeField(default=datetime.now, db_index=True, verbose_name="Дата комментария")
      author = models.ForeignKey(User, null=True, blank=True, verbose_name=("Автор комментария"), on_delete=models.CASCADE)
      post = models.ForeignKey(Blog, verbose_name=("Статья комментария"), on_delete=models.CASCADE)
  
      def __str__(self):
          return f'Комментарий {self.id} {self.author} к {self.post}'
      
      class Meta:
          db_table = "Comment"
          ordering = ["-date"]
          verbose_name = "Комментарий"
          verbose_name_plural = "Комментарии"

admin.site.register(Comment)

# ----- Каталог: категории, товары, картинки -----
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField("Название категории", max_length=120, unique=True)
    slug = models.SlugField("URL (slug)", max_length=140, unique=True, blank=True)
    description = models.TextField("Описание", blank=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE, verbose_name="Категория")
    title = models.CharField("Название товара", max_length=200)
    slug = models.SlugField("URL (slug)", max_length=220, unique=True, blank=True)
    short_description = models.CharField("Краткое описание", max_length=255, blank=True)
    description = models.TextField("Полное описание", blank=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2, default=0.00)
    available = models.BooleanField("В наличии", default=True)
    image = models.ImageField("Главная картинка", upload_to='products/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            # чтобы slug был уникален — добавим id после сохранения, но простая версия:
            self.slug = base
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE, verbose_name="Товар")
    image = models.ImageField("Картинка товара", upload_to='products/gallery/')
    alt_text = models.CharField("Alt текста", max_length=200, blank=True)

    class Meta:
        verbose_name = "Фотография товара"
        verbose_name_plural = "Фотографии товара"

    def __str__(self):
        return f"Image for {self.product.title}"

