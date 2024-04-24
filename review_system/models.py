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
    # product_id = models.CharField(max_length=255)
    product_name = models.CharField(max_length=455 ,default="", blank=True) 
    domain = models.CharField(max_length=255,default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def to_dict(self):
        return {
            'id': self.id,
            'domain' : self.domain,
            'product_name': self.product_name,
            'star_rating' : self.star_rating,
            'review' : self.review,
            'name' : self.name,
            'email' : self.email,
            'image': self.image.url if self.image else '', 
            'created_at' : self.created_at
        }

    def __str__(self):
        return f"{self.star_rating} stars by {self.name}"
    
    class Meta:
        verbose_name = "Product Review"
        verbose_name_plural = "Product Reviews"

class ReviewFormDesign(models.Model):
    id = models.AutoField(primary_key=True)
    field_name = models.CharField(max_length=255)
    color_value = models.CharField(max_length=7)  

    def __str__(self):
        return f"{self.field_name} form"
    
    class Meta:
        verbose_name = "Review Form Design"
        verbose_name_plural = "Review Form Design"

class ReviewListDesign(models.Model):
    id = models.AutoField(primary_key=True)
    element_name = models.CharField(max_length=255)
    color_value = models.CharField(max_length=7)

    def __str__(self):
        return f"{self.element_name} listing"
    
    class Meta:
        verbose_name = "Review Listing Design"
        verbose_name_plural = "Review Listing Design"
