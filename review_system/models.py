from django.db import models
import bcrypt
from django.contrib.auth.hashers import make_password
from django.utils.html import format_html


class ReviewSettings(models.Model):
    auto_approve = models.BooleanField(default=False, null=True)
    domain = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "Review Settings"

    class Meta:
        verbose_name = "Review Setting"
        verbose_name_plural = "Review Settings"


class ProductReviews(models.Model):
    APPROVE = 'approve'
    DISAPPROVE = 'disapprove'
    PENDING = 'pending'
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
    product_name = models.CharField(max_length=455 ,default="", blank=True, null=True) 
    domain = models.CharField(max_length=255, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=255, default="", blank=True, null=True)
    reply_text = models.TextField(blank=True, null=True)
    reply_created_at = models.DateTimeField(blank=True, null=True)

    def to_dict(self):
        return {
            'id': self.id,
            'domain': self.domain,
            'product_name': self.product_name,
            'star_rating': self.star_rating,
            'review': self.review,
            'name': self.name,
            'email': self.email,
            'image': self.image.url if self.image else '',
            'source': self.source,
            'created_at': self.created_at,
            'reply_text': self.reply_text,
            'reply_created_at': self.reply_created_at,
        }

    def __str__(self):
        return "Product Reviews"

    class Meta:
        verbose_name = "Product Review"
        verbose_name_plural = "Product Reviews"


class ReviewFormDesign(models.Model):
    domain = models.CharField(max_length=255, blank=True)
    generate_button = models.CharField(max_length=25, blank=True)
    generate_button_text = models.CharField(max_length=25, blank=True)
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


class Customer(models.Model):
    domain_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    plan_name = models.CharField(max_length=100)
    date_start = models.DateField()
    date_end = models.DateField()
    password = models.CharField(max_length=128, null=True)
    plan_price = models.DecimalField(max_digits=10, decimal_places=2)
    activated = models.BooleanField(default=True)
    profile_img = models.ImageField(upload_to='profile_images/', default='', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith('$2y$'):  # Check if password is already hashed
            salt = bcrypt.gensalt()
            self.password = bcrypt.hashpw(self.password.encode('utf-8'), salt).decode('utf-8')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
