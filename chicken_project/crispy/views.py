from django.shortcuts import render,get_object_or_404,redirect
from .models import Product,Register
from .forms import LoginForm,RegisterForm


def base(request):
    return render(request, 'base.html')
def home(request):
    return render(request, 'home.html')


def profile_details(request):

    q = request.GET.get('q')

    data = Product.objects.all()

    if q:
        data = Product.objects.filter(
            name__icontains=q
        )

    return render( request, 'profile.html', {'data': data}  )


def product_details(request,id):
    i = get_object_or_404(Product, id=id)

    return render(request, 'product_details.html', {'i':i})



def register(request):
    mgs = ""
    if request.method == "POST":
        form = RegisterForm(request.POST)
        email = request.POST.get("email")

        if Register.objects.filter(email = email).exists():
            mgs = "email already exist"
         
        else:
         if form.is_valid():
             form.save()
             return redirect("login")        
    else:
        form = RegisterForm()
    return render(request, 'register.html',{'form':form, "mgs":mgs})




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

    cart = request.session.get('cart', {})

    if str(id) in cart:
        cart[str(id)] += 1
    else:
        cart[str(id)] = 1

    request.session['cart'] = cart

    referer = request.META.get("HTTP_REFERER")
    if referer:
        return redirect(referer)
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