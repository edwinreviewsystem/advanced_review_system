from django.urls import path
from .views import *
from .loginSignup_views import *
from .review_tone_views import *
from django.conf.urls.static import static

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [

    path('', HomePageView.as_view(), name='home'),
    path('apidocs', view_pdf, name='apidocs'),
    path('api/rating', GetChatGPTSuggestions.as_view(), name='generate_suggestions'),
    path('api/review', GetChatGPTReview.as_view(), name='generate_review'),


    path("api/login", MyTokenObtainPairView.as_view(), name="login_api"),
    path("api/login/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/register", RegisterAPIView.as_view(), name="register_api"),
    path("api/logout",LogoutView.as_view(), name="logout_api"),
    
]