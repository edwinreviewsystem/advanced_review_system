
from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class ReviewSerializer(serializers.ModelSerializer):
    # Additional fields that may not be shared between both models
    image = serializers.ImageField(allow_null=True, required=False)
    
    class Meta:
        # We'll dynamically set the model and fields based on the data
        fields = []

    def to_representation(self, instance):
        """
        Custom representation to differentiate between Google_Reviews and ProductReviews
        """
        if isinstance(instance, Google_Reviews):
            # Handling Google_Reviews
            return {
                'place_id': instance.place_id,
                'domain_name': instance.domain_name,
                'google_review_id': instance.google_review_id,
                'author_name': instance.author_name,
                'rating': instance.rating,
                'text': instance.text,
                'time': instance.time,
                'created_at': instance.created_at,
                'status': instance.status
            }
        elif isinstance(instance, ProductReviews):
            # Handling ProductReviews
            return {
                'id': instance.id,
                'star_rating': instance.star_rating,
                'product_name': instance.product_name,
                'domain': instance.domain,
                'name': instance.name,
                'email': instance.email,
                'review': instance.review,
                'image': instance.image.url if instance.image else None,
                'source': instance.source,
                'created_at': instance.created_at,
                'status': instance.status,
                'reply_text' : instance.reply_text,
                'reply_created_at' : instance.reply_created_at
            }

    def create(self, validated_data):
        # Determine which model to use based on fields present in data
        if 'place_id' in validated_data:
            return Google_Reviews.objects.create(**validated_data)
        else:
            return ProductReviews.objects.create(**validated_data)

    def validate_email(self, value):
        """
        Custom email validation for ProductReviews
        """
        try:
            validate_email(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        return value

    def get_fields(self):
        # Set fields dynamically based on input data
        if self.instance and isinstance(self.instance, Google_Reviews):
            self.Meta.model = Google_Reviews
            return {
                'place_id': serializers.CharField(),
                'domain_name': serializers.CharField(),
                'google_review_id': serializers.CharField(),
                'author_name': serializers.CharField(),
                'rating': serializers.IntegerField(),
                'text': serializers.CharField(),
                'time': serializers.DateTimeField(),
            }
        else:
            self.Meta.model = ProductReviews
            return {
                'id': serializers.IntegerField(read_only=True),
                'star_rating': serializers.IntegerField(),
                'product_name': serializers.CharField(allow_null=True),  
                'domain': serializers.CharField(),
                'name': serializers.CharField(),
                'email': serializers.EmailField(),
                'review': serializers.CharField(),
                'image': serializers.ImageField(required=False, allow_null=True),
                'source': serializers.CharField(),
                'created_at': serializers.DateTimeField(read_only=True),
                'reply_text': serializers.CharField(required=False, allow_null=True),  
                'reply_created_at': serializers.DateTimeField(read_only=True),
            }
    
class ReviewFormDesignSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewFormDesign
        fields = ('generate_button', 'generate_button_text', 'button_color', 'button_text_color', 'label_text_color', 'background_color')

class ReviewListDesignSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewListDesign
        fields = ('content_text_color', 'star_rating_color', 'reviewer_name_color', 'review_color')  




class CustomerSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(allow_null=True, required=False)
    last_name = serializers.CharField(allow_null=True, required=False)

    class Meta:
        model = Customer
        fields = '__all__'