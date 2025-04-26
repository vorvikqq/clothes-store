from django.db import models
from django.urls import reverse
from cloudinary.models import CloudinaryField
# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=20, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    sort = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('main:filter-by-category', args=[self.slug])

    class Meta:
        ordering = ['sort']
        indexes = [models.Index(fields=['name'])]
        verbose_name = 'category'
        verbose_name_plural = 'categories'


class Product(models.Model):
    name = models.CharField(max_length=20, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    sort = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')

    image = CloudinaryField('image', folder='products', blank=True, null=True)
    description = models.TextField()

    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(default=0.0, max_digits=4, decimal_places=2)

    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('main:product-detail', kwargs={'slug': self.slug})

    def sell_price(self):
        if self.discount:
            return round(self.price * (1 - self.discount / 100), 2)
        return self.price

    class Meta:
        ordering = ['sort']
        indexes = [models.Index(fields=['id', 'slug']),
                   models.Index(fields=['name']),
                   models.Index(fields=['-created_at'])]
        verbose_name = 'product'
        verbose_name_plural = 'products'
