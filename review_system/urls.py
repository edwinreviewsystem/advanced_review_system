from django.urls import path
from .views import ProductReviewsListAPI, ProductReviewsDetailAPI
from .customization_views import *


urlpatterns = [
    path('reviews', ProductReviewsListAPI.as_view(), name='product_reviews_list'),
    path('reviews/<int:pk>', ProductReviewsDetailAPI.as_view(), name='product_reviews_detail'),
    path('review-form-designs/', ReviewFormDesignListAPI.as_view(), name='review-form-designs'),
    path('review-list-designs/', ReviewListDesignListAPI.as_view(), name='review-list-designs'),
]

