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
    PRIMARY_BUTTON_POSITION_CHOICES = [
        ("Middle Left", "Middle Left"),
        ("Middle Right", "Middle Right"),
        ("Top Left", "Top Left"),
        ("Top Middle", "Top Middle"),
        ("Top Right", "Top Right"),
        ("Bottom Left", "Bottom Left"),
        ("Bottom Middle", "Bottom Middle"),
        ("Bottom Right", "Bottom Right"),
    ]

    domain = models.CharField(max_length=255, blank=True)
    content_text_color = models.CharField(max_length=25, blank=True)
    star_rating_color = models.CharField(max_length=25, blank=True)
    reviewer_name_color = models.CharField(max_length=25, blank=True)
    review_color = models.CharField(max_length=25, blank=True)
    primary_btn_color = models.CharField(max_length=25, null=True, blank=True, verbose_name="Reviews Button Color")
    btn_border_radius = models.CharField(max_length=25, null=True, blank=True, verbose_name="Reviews Button Corners")
    primary_button_position = models.CharField(max_length=25, null=True, blank=True, choices=PRIMARY_BUTTON_POSITION_CHOICES, default="Bottom Left", verbose_name="Reviews Button Position")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Review List Design"
        verbose_name_plural = "Review List Design"


class Google_Reviews(models.Model):
    APPROVE = 'approve'
    DISAPPROVE = 'disapprove'
    PENDING = 'pending'
    STATUS_CHOICES = [
        (APPROVE, 'Approve'),
        (DISAPPROVE, 'Disapprove'),
        (PENDING, 'Pending')
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=APPROVE)
    place_id = models.CharField(max_length=255)  
    domain_name = models.CharField(max_length=255) 
    google_review_id = models.CharField(max_length=255, unique=True) 
    author_name = models.CharField(max_length=255) 
    rating = models.IntegerField() 
    text = models.TextField() 
    time = models.DateTimeField() 
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return f"Review by {self.author_name} on {self.domain_name}"

    class Meta:
        verbose_name = "Google Review"

class Plans(models.Model):
    name = models.CharField(max_length=255)
    features = models.CharField(max_length=1000, null=True, blank=True)
    duration = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=3)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.duration})"
    
    class Meta:
        verbose_name = "Plan"
        verbose_name_plural = "Plans"

class Customer(models.Model):
    plan = models.ForeignKey(Plans, on_delete=models.SET_NULL, default=1, null=True, verbose_name="Plan Info")
    domain_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    date_start = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)
    password = models.CharField(max_length=128, null=True)
    plan_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    activated = models.BooleanField(default=True)
    profile_img = models.ImageField(upload_to='profile_images/', default='', null=True, blank=True)
    platform = models.CharField(max_length=255, blank=True, null=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith('$2y$'):  # Check if password is already hashed
            salt = bcrypt.gensalt()
            self.password = bcrypt.hashpw(self.password.encode('utf-8'), salt).decode('utf-8')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

# class Sites(models.Model):
#     customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
#     plan_id = models.ForeignKey(Plans, on_delete=models.SET_NULL)
#     domain = models.CharField(max_length=255, unique=True)
#     created_at = models.DateTimeField(auto_now_add=True) 
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return "sites"
    
#     class Meta:
#         verbose_name = "Site"
#         verbose_name_plural = "Sites"