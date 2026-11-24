from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    discription = models.TextField()
    image = models.ImageField(upload_to='product/')
    category = models.CharField(max_length=50, default='Crunchy')

    def __str__(self):
        return self.name
    
class Register(models.Model):
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=150)

    def __str__(self):
       return self.username