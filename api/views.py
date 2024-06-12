from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import AIReviewSerializer
import openai
import re, json
from django.conf import settings
from django.views.generic import TemplateView
from django.conf import settings
from django.http import HttpResponse
import logging

logger = logging.getLogger('api')
logger.setLevel(logging.DEBUG)

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)

        token['username'] = user.username
        return token
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class HomePageView(TemplateView):
    template_name = 'home.html'

def view_pdf(request):
    pdf_file_path = 'static/Review_System_APIDocs.pdf'  
    with open(pdf_file_path, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'filename="apidocs.pdf"'
        return response

class GetChatGPTSuggestions(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = AIReviewSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            star_rating = serializer.validated_data['star_rating']
            product_name = serializer.validated_data['product_name']
            review_tone = serializer.validated_data['review_tone']


            suggestions = self.get_chatgpt_suggestions(star_rating, product_name, review_tone)
            return Response({'suggestions': suggestions}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


    def get_chatgpt_suggestions(self, star_rating,product_name,review_tone):
        openai.api_key = settings.OPEN_API_KEY
        prompt = f"User gives {star_rating} stars to {product_name}. Generate 9-11 best describing words in a {review_tone} tone. Ignore description and should be in the array format. withouy any extra symbol and in a single line."

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for reviewing products/services."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=60
        )

        

        suggestions = response['choices'][0]['message']['content'].strip()
        
        # suggestions = suggestions.strip('[]')
        # suggestions = [s.strip('"').strip("'") for s in suggestions.split(", ")]
        # suggestions = json.loads(suggestions)
        # return suggestions
        suggestions = suggestions.strip("[]").replace('\n', '').replace('"', '').replace("'", "")
        suggestions = [s.strip() for s in suggestions.split(",")]
        return suggestions


class GetChatGPTReview(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = AIReviewSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            star_rating = serializer.validated_data['star_rating']
            user_selected_words = serializer.validated_data['user_selected_words']
            product_name = serializer.validated_data['product_name']
            
            review = self.get_chatgpt_review(star_rating, user_selected_words, product_name)
            return Response({'AIreview': review}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

    def get_chatgpt_review(self, star_rating, user_selected_words, product_name):
        openai.api_key = settings.OPEN_API_KEY
        prompt = f"User give {star_rating} stars selected {user_selected_words} best describing words for {product_name}. Provide a detailed 80-100 words review on these basis for {product_name}, in easy real language. Ignore description."
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for reviewing products/services."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )
        review = response['choices'][0]['message']['content']
        return review
      
