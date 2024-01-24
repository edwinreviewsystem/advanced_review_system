from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import ProductReviewSerializer
import openai
from django.conf import settings
from django.views.generic import TemplateView
import json
import os
from django.conf import settings
from django.http import Http404
from django.http import FileResponse
from django.http import HttpResponse


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
    pdf_file_path = 'static/Review_System_Docs.pdf'  
    with open(pdf_file_path, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'filename="apidocs.pdf"'
        return response

class GetChatGPTSuggestions(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = ProductReviewSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            star_rating = serializer.validated_data['star_rating']
            product_name = serializer.validated_data['product_name']

            suggestions = self.get_chatgpt_suggestions(star_rating, product_name)
            return Response({'suggestions': suggestions}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

    def get_chatgpt_suggestions(self, star_rating,product_name):
        openai.api_key = settings.OPEN_API_KEY
        prompt = f"User rated the product:{product_name} with {star_rating} stars. Generate 8-10 best describing words for {star_rating} of {product_name}, Ignore description and should be in the array format."

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for the product review system."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=60
        )

        suggestions = response['choices'][0]['message']['content']
        suggestions_list = json.loads(suggestions)
         # suggestions = "Neutral, average, satisfactory, acceptable, standard, decent, usual"  
        return suggestions_list
       
       


class GetChatGPTReview(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = ProductReviewSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            star_rating = serializer.validated_data['star_rating']
            user_word = serializer.validated_data['user_word']
            product_name = serializer.validated_data['product_name']
            
            review = self.get_chatgpt_review(star_rating, user_word, product_name)
            return Response({'review': review}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



    def get_chatgpt_review(self, star_rating, user_word, product_name):
        openai.api_key = settings.OPEN_API_KEY
        prompt = f"User selected {user_word} as best describing words for {product_name} and rated {star_rating} stars for review.Only provide a detailed 80-100 words review based on {product_name} in easy language. Ignore description."

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for a product review system."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )
        review = response['choices'][0]['message']['content']
        # review = "The product was average in terms of performance. It did the job adequately. It was satisfactory and decent overall. The quality and durability were moderate, and it seemed to hold up fine under regular use. The features and functionality were acceptable, but there was nothing that stood out. I would give it 3 stars because it met my basic needs, but I wasn't overly impressed. If you're looking for a basic, no-frills product, this would be a decent choice."
        return review
      
