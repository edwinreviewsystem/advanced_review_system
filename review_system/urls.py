from django.urls import path
from .views import ProductReviewsListAPI, ProductReviewsDetailAPI


urlpatterns = [
    path('reviews', ProductReviewsListAPI.as_view(), name='product_reviews_list'),
    path('reviews/<int:pk>', ProductReviewsDetailAPI.as_view(), name='product_reviews_detail'),
    # path('reviews/<str:pk>', ProductReviewsDetailAPI.as_view(), name='product_reviews_detail'),
]

