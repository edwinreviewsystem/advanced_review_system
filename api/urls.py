from django.urls import path
from .views import *
from .loginSignup_views import *

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('rating/', GetChatGPTSuggestions.as_view(), name='submit_rating'),
    path('review/', GetChatGPTReview.as_view(), name='generate_review'),

    path("login/", TokenObtainPairView.as_view(), name="login_api"),
    path("register/", RegisterAPIView.as_view(), name="register_api"),
    

]
