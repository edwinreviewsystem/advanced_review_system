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
    path('apidocs', view_pdf, name='view_apidocs'),
    path('api/rating', GetChatGPTSuggestions.as_view(), name='submit_rating'),
    path('api/review', GetChatGPTReview.as_view(), name='generate_review'),
    path('api/review-tones', ReviewToneListAPIView.as_view(), name='review-tone-list'),
    path('api/review-tones/create', ReviewToneCreateAPIView.as_view(), name='review-tone-create'),
    path('api/review-tones/<int:pk>', ReviewToneDetailAPIView.as_view(), name='review-tone-detail'),


    path("api/login", MyTokenObtainPairView.as_view(), name="login_api"),
    path("api/login/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/register", RegisterAPIView.as_view(), name="register_api"),
    path("api/logout",LogoutView.as_view(), name="logout_api"),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)