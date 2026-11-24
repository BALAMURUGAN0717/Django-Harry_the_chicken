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

    lollipop_id = lollipop.id if lollipop else 1
    tandoori_id = tandoori.id if tandoori else 1
    grill_id = grill.id if grill else 1

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
        data = data.filter(name__icontains=q)
    if category:
        data = data.filter(category__iexact=category)

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
        email = request.POST.get("email")

        if Register.objects.filter(email=email).exists():
            mgs = "email already exist"
        else:
            if form.is_valid():
                form.save()
                return redirect("login")        
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form, "mgs": mgs})


def login(request):
    mgs = ""
    form = LoginForm()

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = Register.objects.get(username=username, password=password)
            request.session["username"] = user.username
            response = redirect('home')
            response.set_cookie("username", user.username)
            return response
        except Register.DoesNotExist:
            mgs = "invalid username or password"

    return render(request, 'login.html', {'form': form, 'mgs': mgs})


def logout(request):
    request.session.flush()
    return redirect("login")


def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)
    cart = request.session.get('cart', {})

    if str(id) in cart:
        cart[str(id)] += 1
    else:
        cart[str(id)] = 1

    request.session['cart'] = cart
    total_count = sum(cart.values()) if isinstance(cart, dict) else 0

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
    str_id = str(id)

    if str_id in cart:
        if cart[str_id] > 1:
            cart[str_id] -= 1
        else:
            del cart[str_id]
        request.session['cart'] = cart

    total_count = sum(cart.values()) if isinstance(cart, dict) else 0

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1':
        return JsonResponse({
            'status': 'success',
            'cart_count': total_count,
        })

    return redirect('cart')


def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for id, quantity in cart.items():
        try:
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            continue

        subtotal = product.price * quantity
        total += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })


def remove_cart(request, id):
    cart = request.session.get('cart', {})

    if str(id) in cart:
        del cart[str(id)]

    request.session['cart'] = cart
    return redirect('cart')
