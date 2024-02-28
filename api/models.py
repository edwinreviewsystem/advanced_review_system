from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class ReviewTone(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class ProductReview(models.Model):
    STAR_CHOICES = [
        (1, '1 star'),
        (2, '2 stars'),
        (3, '3 stars'),
        (4, '4 stars'),
        (5, '5 stars'),
    ]

    star_rating = models.IntegerField(choices=STAR_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    user_word = models.CharField(max_length=200, default=None)
    product_name = models.CharField(max_length=255) 
    generated_review = models.TextField(blank=True, null=True)
    review_tone = models.ForeignKey(ReviewTone, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Review - {self.star_rating} stars"

