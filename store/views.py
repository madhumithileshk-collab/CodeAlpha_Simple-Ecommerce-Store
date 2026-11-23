
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Order, OrderItem

def home(request):
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products})

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'store/detail.html', {'product': product})

def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)
    cart = request.session.get('cart', {})
    product_id = str(id)

    cart[product_id] = cart.get(product_id, 0) + 1
    request.session['cart'] = cart

    return redirect('cart')

def cart(request):
    cart_data = request.session.get('cart', {})
    cart_items = []
    total = 0

    for product_id, quantity in cart_data.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal = product.price * quantity
        total += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'store/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'store/login.html')

from django.db import transaction

def checkout(request):
    cart_data = request.session.get('cart', {})

    if not cart_data:
        return redirect('cart')

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        customer_email = request.POST.get('customer_email')

        total = 0
        for product_id, quantity in cart_data.items():
            product = get_object_or_404(Product, id=product_id)
            total += product.price * quantity

        order = Order.objects.create(
            customer_name=customer_name,
            customer_email=customer_email,
            total_amount=total
        )

        for product_id, quantity in cart_data.items():
            product = get_object_or_404(Product, id=product_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity
            )

        request.session['cart'] = {}

        return render(request, 'store/success.html', {'order': order})

    return render(request, 'store/checkout.html')

