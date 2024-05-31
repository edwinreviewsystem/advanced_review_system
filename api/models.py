from django.db import models
from django.contrib.auth.models import User
# Create your models here.


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

    # user = models.ForeignKey(User, on_delete=models.CASCADE, null= True)
    star_rating = models.IntegerField(choices=STAR_CHOICES)
    review_tone = models.CharField(max_length=255, blank=True, null=True)
    product_name = models.TextField(blank=True, null=True) 
    user_selected_words = models.CharField(max_length=455, default=None)
    generated_review = models.TextField(blank=True, null=True)
   
    def __str__(self):
        return "AI Reviews"
    
    class Meta:
        db_table = 'api_aireview' 

