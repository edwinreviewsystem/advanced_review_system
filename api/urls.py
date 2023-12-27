from django.urls import path
from .views import *
from .loginSignup_views import *

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('api/rating', GetChatGPTSuggestions.as_view(), name='submit_rating'),
    path('api/review', GetChatGPTReview.as_view(), name='generate_review'),

    path("api/login", TokenObtainPairView.as_view(), name="login_api"),
    path("api/register", RegisterAPIView.as_view(), name="register_api"),
    path("api/logout",LogoutView.as_view(), name="logout_api"),
    
]
