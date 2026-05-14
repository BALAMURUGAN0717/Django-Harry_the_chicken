from django.shortcuts import render,get_object_or_404
from .models import Product

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

    return render(
        request,
        'product.html',
        {'data': data}
    )