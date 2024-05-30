from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class ProductReviews(models.Model):
    
    APPROVE = 'approve'
    DISAPPROVE = 'disapprove'
    PENDING = 'Pending'
    STATUS_CHOICES = [
        (APPROVE, 'Approve'),
        (DISAPPROVE, 'Disapprove'),
        (PENDING, 'Pending')
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    star_rating = models.IntegerField()
    review = models.TextField()
    email = models.EmailField()
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='uploaded_images/', default='', blank=True)
    product_name = models.CharField(max_length=455 ,default="", blank=True, null =True) 
    domain = models.CharField(max_length=255,default="")
    created_at = models.DateTimeField(auto_now_add=True)

    reply_text = models.TextField(blank=True, null=True)
    reply_created_at = models.DateTimeField(blank=True, null=True)
    auto_approve = models.BooleanField(default=0)

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
            'created_at' : self.created_at,
            'reply_text' : self.reply_text,
            'reply_created_at': self.reply_created_at,
        }

    def __str__(self):
        return "Product Reviews"
    
    class Meta:
        verbose_name = "Product Review"
        verbose_name_plural = "Product Reviews"
  

class ReviewFormDesign(models.Model):
    domain = models.CharField(max_length=255, blank=True)
    button_color = models.CharField(max_length=25, blank=True)
    button_text_color = models.CharField(max_length=25, blank=True)
    label_text_color = models.CharField(max_length=25, blank=True)
    background_color = models.CharField(max_length=25, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Review Form Design"
        verbose_name_plural = "Review Form Design"

class ReviewListDesign(models.Model):
    domain = models.CharField(max_length=255, blank=True)
    content_text_color = models.CharField(max_length=25, blank=True)
    star_rating_color = models.CharField(max_length=25, blank=True)
    reviewer_name_color = models.CharField(max_length=25, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Review List Design"
        verbose_name_plural = "Review List Design"


 
