"""
Definition of urls for DnDShop.
"""

from datetime import datetime
from django.urls import path
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from app import forms, views

from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings


urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('links/', views.links, name='links'),
    path('about/', views.about, name='about'),
    path('pool/', views.pool, name='pool'),
    path('registration/', views. registration, name= 'registration'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<int:pk>/', views.blog_detail, name='blog_detail'),
    path('newpost/', views.newpost, name='newpost'),
    path('videopost/', views.videopost, name='videopost'),
    path('catalog/', views.catalog, name='catalog'),
    path('catalog/<slug:category_slug>/', views.category_view, name='category'),
    path('product/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/', views.cart_update, name='cart_update'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('orders/', views.orders_manager, name='orders_manager'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),

    path('login/',
         LoginView.as_view
         (
             template_name='app/login.html',
             authentication_form=forms.BootstrapAuthenticationForm,
             extra_context=
             {
                 'title': 'Вход',
                 'year' : datetime.now().year,
             }
         ),
         name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('admin/', admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) #Добавление строк шаблонов URL для загрузки файлов в папку media
urlpatterns += staticfiles_urlpatterns()
