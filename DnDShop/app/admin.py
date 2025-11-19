from django.contrib import admin
from .models import Category, Product, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'available', 'created_at')
    list_filter = ('available', 'category')
    search_fields = ('title', 'description', 'short_description')
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProductImageInline]
