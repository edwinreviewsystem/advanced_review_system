from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# class ReviewTone(models.Model):
#     name = models.CharField(max_length=255, unique=True)

#     def __str__(self):
#         return self.name


class AIReview(models.Model):
    STAR_CHOICES = [
        (1, '1 star'),
        (2, '2 stars'),
        (3, '3 stars'),
        (4, '4 stars'),
        (5, '5 stars'),
    ]
    REVIEW_TONE_CHOICES = [
    ('Professional and Informative', 'Professional and Informative'),
    ('Casual and Conversational', 'Casual and Conversational'),
    ('Critical and Honest', 'Critical and Honest'),
    ('Casual and Conservative', 'Casual and Conservative'),
    ]


    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    star_rating = models.IntegerField(choices=STAR_CHOICES)
    review_tone = models.CharField(max_length=150, choices=REVIEW_TONE_CHOICES, blank=True, null=True)
    product_name = models.TextField() 
    # domain = models.CharField()
    user_selected_words = models.CharField(max_length=200, default=None)
    generated_review = models.TextField(blank=True, null=True)
   
    def __str__(self):
        return f"Review - {self.star_rating}stars"

