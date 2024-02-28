from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class ProductReviews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null= True)
    star_rating = models.IntegerField()
    review = models.TextField()
    email = models.EmailField()
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='uploaded_images/', default='')
    product_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.star_rating} stars by {self.name}"
    
    class Meta:
        verbose_name = "Product Review"
        verbose_name_plural = "Product Reviews"
