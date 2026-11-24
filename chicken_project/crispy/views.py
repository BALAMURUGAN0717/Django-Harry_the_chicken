from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Product, Register
from .forms import LoginForm, RegisterForm


def base(request):
    return render(request, 'base.html')


def home(request):
    # Retrieve specific products for the 3 Read More buttons
    lollipop = (
        Product.objects.filter(name__iexact="Chicken Lollipop").first()
        or Product.objects.filter(name__icontains="Lollipop").first()
    )
    tandoori = (
        Product.objects.filter(name__iexact="Chicken Tandoori").first()
        or Product.objects.filter(name__iexact="Half Tandoori Chicken").first()
        or Product.objects.filter(name__icontains="Tandoori").first()
    )
    grill = (
        Product.objects.filter(name__iexact="Grill Tandoori").first()
        or Product.objects.filter(name__iexact="Juicy Grilled Chicken").first()
        or Product.objects.filter(name__icontains="Grill").first()
    )

    first_product = Product.objects.first()
    fallback_id = first_product.id if first_product else 1

    lollipop_id = lollipop.id if lollipop else fallback_id
    tandoori_id = tandoori.id if tandoori else fallback_id
    grill_id = grill.id if grill else fallback_id

    menu_products = Product.objects.all().order_by('id')

    return render(request, 'home.html', {
        'menu_products': menu_products,
        'lollipop_id': lollipop_id,
        'tandoori_id': tandoori_id,
        'grill_id': grill_id,
    })


def profile_details(request):
    q = request.GET.get('q')
    category = request.GET.get('category')
    data = Product.objects.all()

    if q:
        data = data.filter(name__icontains=q.strip())
    if category:
        data = data.filter(category__iexact=category.strip())

    return render(request, 'profile.html', {
        'data': data,
        'selected_category': category
    })


def product_details(request, id):
    i = get_object_or_404(Product, id=id)
    return render(request, 'product_details.html', {'i': i})


def register(request):
    mgs = ""
    if request.method == "POST":
        form = RegisterForm(request.POST)
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        if not username or not email or not password:
            mgs = "All fields are required"
        elif Register.objects.filter(email=email).exists():
            mgs = "Email already exists"
        elif Register.objects.filter(username=username).exists():
            mgs = "Username already exists"
        else:
            if form.is_valid():
                try:
                    user = form.save(commit=False)
                    user.username = username
                    user.email = email
                    user.password = password
                    user.save()
                    return redirect("login")
                except Exception as e:
                    mgs = f"Registration error: {e}"
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form, "mgs": mgs})


def login(request):
    mgs = ""
    form = LoginForm()

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        # Safely query user and handle potential duplicates or non-existent user
        user = Register.objects.filter(username=username).first()
        if user and user.password == password:
            request.session["username"] = user.username
            request.session.modified = True
            response = redirect('home')
            response.set_cookie("username", user.username, max_age=86400 * 30, httponly=True)
            return response
        else:
            mgs = "Invalid username or password"

    return render(request, 'login.html', {'form': form, 'mgs': mgs})


def logout(request):
    request.session.flush()
    response = redirect("login")
    response.delete_cookie("username")
    return response


def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)
    cart = request.session.get('cart', {})
    if not isinstance(cart, dict):
        cart = {}

    str_id = str(id)
    cart[str_id] = cart.get(str_id, 0) + 1
    request.session['cart'] = cart
    request.session.modified = True
    total_count = sum(cart.values())

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1':
        return JsonResponse({
            'status': 'success',
            'cart_count': total_count,
            'product_id': product.id,
            'product_name': product.name,
            'product_price': str(product.price),
            'message': f'{product.name} added to cart!'
        })

    referer = request.META.get("HTTP_REFERER")
    if referer:
        return redirect(referer)
    return redirect('cart')


def decrease_cart(request, id):
    cart = request.session.get('cart', {})
    if not isinstance(cart, dict):
        cart = {}

    str_id = str(id)
    if str_id in cart:
        if cart[str_id] > 1:
            cart[str_id] -= 1
        else:
            del cart[str_id]
        request.session['cart'] = cart
        request.session.modified = True

    total_count = sum(cart.values())

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1':
        return JsonResponse({
            'status': 'success',
            'cart_count': total_count,
        })

    return redirect('cart')


def cart_view(request):
    cart = request.session.get('cart', {})
    if not isinstance(cart, dict):
        cart = {}

    cart_items = []
    total = 0

    for item_id, quantity in list(cart.items()):
        try:
            product = Product.objects.get(id=item_id)
        except (Product.DoesNotExist, ValueError):
            continue

        try:
            qty = int(quantity)
        except (ValueError, TypeError):
            qty = 1

        subtotal = product.price * qty
        total += subtotal

        cart_items.append({
            'product': product,
            'quantity': qty,
            'subtotal': subtotal
        })

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })


def remove_cart(request, id):
    cart = request.session.get('cart', {})
    if isinstance(cart, dict):
        str_id = str(id)
        if str_id in cart:
            del cart[str_id]
            request.session['cart'] = cart
            request.session.modified = True
    return redirect('cart')
