"""
Definition of views.
"""

from datetime import datetime
from django.http import HttpRequest, HttpResponseForbidden
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from .models import Blog, Comment, Category, Product, Order, OrderItem
from .forms import CommentForm
from .forms import BlogForm
from decimal import Decimal
from django.urls import reverse
from .utils import client_required, manager_required


# ---- дополнительные импорты для регистрации/групп ----
from django.contrib.auth import login
from django.contrib.auth.models import Group

def home(request):
    """Главная страница: добавляем последние 3 новости (посты блога)."""
    assert isinstance(request, HttpRequest)
    latest_posts = Blog.objects.all()[:3]   # модель Blog есть в models.py
    return render(
        request,
        'app/index.html',
        {
            'title': 'Главная',
            'year': datetime.now().year,
            'latest_posts': latest_posts,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Контакты',
            'message':'Страница с нашими контактами.',
            'year':datetime.now().year,
        }
    )

def registration(request):
    """
    Регистрация пользователя.
    После создания пользователь автоматически добавляется в группу 'Client' и производится автологин.
    """
    assert isinstance(request, HttpRequest)
    if request.method == "POST":  # после отправки формы
        regform = UserCreationForm(request.POST)
        if regform.is_valid():  # валидация полей формы
            reg_f = regform.save(commit=False)  # не сохраняем автоматически данные формы
            reg_f.is_staff = False  # запрещен вход в административный раздел
            reg_f.is_active = True  # активный пользователь
            reg_f.is_superuser = False  # не является суперпользователем
            reg_f.date_joined = datetime.now()  # дата регистрации
            reg_f.last_login = datetime.now()  # дата последней авторизации
            reg_f.save()  # сохраняем изменения после добавления данных

            # Добавляем пользователя в группу Client (создаст группу, если её нет)
            client_group, _ = Group.objects.get_or_create(name='Client')
            reg_f.groups.add(client_group)
            reg_f.save()

            # Автоматический вход после регистрации (опционально, выполнено по умолчанию)
            login(request, reg_f)

            return redirect('home')  # переадресация на главную страницу после регистрации

    else:
        regform = UserCreationForm()  # создание объекта формы для ввода данных нового пользователя
    return render(
        request,
        'app/registration.html',
        {
            'regform': regform,  # передача формы в шаблон веб-страницы
            'year': datetime.now().year,
        }
    )

def blog_list(request):
     posts = Blog.objects.all()
     return render(request, 'app/blog_list.html', {'posts': posts})
 
def blog_detail(request, pk):
    post = get_object_or_404(Blog, pk=pk)
    comments = Comment.objects.filter(post=pk)
 
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment_f = form.save(commit=False)
            comment_f.author = request.user
            comment_f.date = datetime.now()
            comment_f.post = post
            comment_f.save()
 
            return redirect('blog_detail', pk=post.id)
    else:
        form = CommentForm()
    return render(
        request,
        'app/blog_detail.html',
        {
            'post': post,
            'comments': comments,
            'form': form,
            'year': datetime.now().year
        }
    )

def newpost(request):
    """Renders the newpost page."""
    assert isinstance(request, HttpRequest)

    if request.method == "POST":
        blogform = BlogForm(request.POST, request.FILES)
        if blogform.is_valid():
            blog_f = blogform.save(commit=False)
            blog_f.posted = datetime.now()
            blog_f.autor = request.user
            blog_f.save()

            return redirect('blog_list')

    else:
        blogform = BlogForm()

    return render(
        request,
        'app/newpost.html',
        {
            'blogform': blogform,
            'title': 'Добавить статью блога',
            'year': datetime.now().year,
        }
    )

def catalog(request):
    """Простейший каталог — список категорий (заглушка)."""
    assert isinstance(request, HttpRequest)
    try:
        categories = Category.objects.all()
    except Exception:
        categories = []
    return render(
        request,
        'app/catalog.html',
        {
            'title': 'Каталог',
            'categories': categories,
            'year': datetime.now().year,
        }
    )

def category_view(request, category_slug):
    """Страница категории: список товаров в категории."""
    assert isinstance(request, HttpRequest)
    category = get_object_or_404(Category, slug=category_slug)
    products = category.products.filter(available=True).order_by('-created_at')
    return render(request, 'app/category.html', {
        'title': category.name,
        'category': category,
        'products': products,
        'year': datetime.now().year,
    })


def product_detail(request, product_slug):
    """Страница одного товара."""
    assert isinstance(request, HttpRequest)
    product = get_object_or_404(Product, slug=product_slug, available=True)
    images = product.images.all()
    return render(request, 'app/product_detail.html', {
        'title': product.title,
        'product': product,
        'images': images,
        'year': datetime.now().year,
    })

# ---- Корзина (session-based) ----
@client_required
def cart_add(request, product_id):
    """
    Добавить товар в корзину (POST). Доступ — только для клиентов.
    Форму отправляйте методом POST (product_detail.html уже посылает POST).
    """
    assert isinstance(request, HttpRequest)
    product = get_object_or_404(Product, pk=product_id, available=True)

    # Получаем количество из POST (если нет — 1)
    qty = 1
    if request.method == 'POST':
        try:
            qty = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            qty = 1
    if qty < 1:
        qty = 1

    cart = request.session.get('cart', {})
    pid = str(product_id)
    cart[pid] = cart.get(pid, 0) + qty
    request.session['cart'] = cart
    request.session.modified = True

    # Можно показать флеш-сообщение — здесь просто редирект на корзину
    return redirect('cart')


@client_required
def cart_view(request):
    """
    Просмотр корзины: показывает товары, количество, подитоги и итог.
    Доступ — только для клиентов.
    """
    assert isinstance(request, HttpRequest)
    cart = request.session.get('cart', {})

    items = []
    total = Decimal('0.00')

    for pid, qty in cart.items():
        try:
            product = Product.objects.get(pk=int(pid))
        except (Product.DoesNotExist, ValueError):
            continue
        subtotal = (product.price or Decimal('0.00')) * int(qty)
        items.append({
            'product': product,
            'quantity': int(qty),
            'subtotal': subtotal,
        })
        total += subtotal

    return render(request, 'app/cart.html', {
        'title': 'Корзина',
        'items': items,
        'total': total,
        'year': datetime.now().year,
    })


@client_required
def cart_update(request):
    """
    Обновление/удаление позиции корзины (POST).
    Ожидает поля: action (update/remove), product_id, quantity (для update).
    """
    assert isinstance(request, HttpRequest)
    if request.method != 'POST':
        return redirect('cart')

    cart = request.session.get('cart', {})

    action = request.POST.get('action')
    pid = request.POST.get('product_id')

    if not pid:
        return redirect('cart')

    if action == 'update':
        try:
            qty = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            qty = 1
        if qty > 0:
            cart[str(pid)] = qty
        else:
            cart.pop(str(pid), None)

    elif action == 'remove':
        cart.pop(str(pid), None)

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')

@client_required
def my_orders(request):
    """Список заказов текущего клиента."""
    assert isinstance(request, HttpRequest)
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'app/my_orders.html', {
        'title': 'Мои заказы',
        'orders': orders,
        'year': datetime.now().year,
    })


# === Менеджер: управление заказами ===
@manager_required
def orders_manager(request):
    """
    Менеджер: просмотр всех заказов и возможность менять статус через POST.
    """
    assert isinstance(request, HttpRequest)
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        try:
            order = Order.objects.get(pk=int(order_id))
            if new_status in dict(Order.STATUS_CHOICES).keys():
                order.status = new_status
                order.save()
        except Exception:
            pass
        return redirect('orders_manager')

    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'app/orders_manager.html', {
        'title': 'Заказы (менеджер)',
        'orders': orders,
        'year': datetime.now().year,
    })


# === Checkout (пока простая заглушка) ===
@client_required
def checkout(request):
    """
    Страница оформления заказа.
    GET: показать форму; POST: создать Order & OrderItem и очистить корзину.
    """
    assert isinstance(request, HttpRequest)

    if request.method == 'POST':
        # собираем данные доставки из формы
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        comment = request.POST.get('comment', '').strip()

        cart = request.session.get('cart', {})
        if not cart:
            # корзина пуста — перенаправляем на корзину
            return redirect('cart')

        # создаём заказ
        order = Order.objects.create(
            customer=request.user,
            full_name=full_name,
            phone=phone,
            address=address,
            comment=comment,
            status=Order.STATUS_NEW
        )

        total = Decimal('0.00')
        for pid, qty in cart.items():
            try:
                product = Product.objects.get(pk=int(pid))
            except (Product.DoesNotExist, ValueError):
                continue
            price = product.price or Decimal('0.00')
            qty_i = int(qty)
            OrderItem.objects.create(order=order, product=product, quantity=qty_i, price=price)
            total += price * qty_i

        order.total_price = total
        order.save()

        # очищаем корзину
        request.session['cart'] = {}
        request.session.modified = True

        return redirect('my_orders')

    # GET — собрать данные корзины и показать форму (как раньше)
    cart = request.session.get('cart', {})
    items = []
    total = Decimal('0.00')
    for pid, qty in cart.items():
        try:
            product = Product.objects.get(pk=int(pid))
        except (Product.DoesNotExist, ValueError):
            continue
        subtotal = (product.price or Decimal('0.00')) * int(qty)
        items.append({'product': product, 'quantity': int(qty), 'subtotal': subtotal})
        total += subtotal

    return render(request, 'app/checkout.html', {
        'title': 'Оформление заказа',
        'items': items,
        'total': total,
        'year': datetime.now().year,
    })

@client_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    # разрешаем просмотр владельцу заказа, менеджеру и суперюзеру
    from .utils import is_manager
    if not (request.user.is_superuser or is_manager(request.user) or order.customer == request.user):
        return HttpResponseForbidden("Доступ запрещён")
    items = order.items.all()
    return render(request, 'app/order_detail.html', {'order': order, 'items': items})

