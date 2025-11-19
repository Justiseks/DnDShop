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


from django.conf import settings
from decimal import Decimal
from django.db import models
from django.utils import timezone

# ---- Заказы ----
class Order(models.Model):
    STATUS_NEW = 'NEW'
    STATUS_PROCESSING = 'PROCESSING'
    STATUS_SHIPPED = 'SHIPPED'
    STATUS_CANCELLED = 'CANCELLED'
    STATUS_CHOICES = [
        (STATUS_NEW, 'Новый'),
        (STATUS_PROCESSING, 'В обработке'),
        (STATUS_SHIPPED, 'Отправлен'),
        (STATUS_CANCELLED, 'Отменён'),
    ]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='orders',
                                 on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Клиент")
    created_at = models.DateTimeField(verbose_name="Создан", default=timezone.now)
    status = models.CharField(verbose_name="Статус", max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    total_price = models.DecimalField(verbose_name="Итоговая сумма", max_digits=10, decimal_places=2, default=0)
    full_name = models.CharField(verbose_name="ФИО получателя", max_length=200, blank=True)
    phone = models.CharField(verbose_name="Телефон", max_length=50, blank=True)
    address = models.TextField(verbose_name="Адрес доставки", blank=True)
    comment = models.TextField(verbose_name="Комментарий к заказу", blank=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.id} — {self.created_at.date()} — {self.status}"

    def recalc_total(self):
        """Пересчитать total_price по связанным OrderItem"""
        total = Decimal('0.00')
        for item in self.items.all():
            total += (item.price * item.quantity)
        self.total_price = total
        self.save(update_fields=['total_price'])

    def get_total_display(self):
        return f"{self.total_price:.2f}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name="Заказ")
    product = models.ForeignKey('Product', related_name='order_items', on_delete=models.SET_NULL, null=True, verbose_name="Товар")
    quantity = models.PositiveIntegerField(verbose_name="Количество", default=1)
    price = models.DecimalField(verbose_name="Цена на момент заказа", max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        prod = self.product.title if self.product else "удален"
        return f"{prod} x {self.quantity}"

    def save(self, *args, **kwargs):
        # если цена не указана, взять текущую цену товара
        if (not self.price or self.price == Decimal('0.00')) and self.product:
            self.price = self.product.price
        super().save(*args, **kwargs)

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=OrderItem)
def orderitem_saved(sender, instance, created, **kwargs):
    if instance.order:
        instance.order.recalc_total()

@receiver(post_delete, sender=OrderItem)
def orderitem_deleted(sender, instance, **kwargs):
    if instance.order:
        instance.order.recalc_total()

