from django.urls import path
from .views import *
from .customization_views import *


urlpatterns = [
    path('reviews', ProductReviewsListAPI.as_view(), name='product_reviews_list'),
    path('reviews/<int:pk>', ProductReviewsDetailAPI.as_view(), name='product_reviews_detail'),
    path('get-customize-css', CustomizationAPIView.as_view(), name='get_customize_css'),
    path('post-webhook/', CustomerCreateAPIView.as_view(), name='create-customer'),
]

