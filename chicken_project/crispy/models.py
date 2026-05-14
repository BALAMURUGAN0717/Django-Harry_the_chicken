from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    discription = models.TextField()
    image = models.ImageField(upload_to='product/')

    def __str__(self):
        return self.name