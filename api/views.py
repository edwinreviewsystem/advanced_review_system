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
            meta_info = request.data['meta_info']
            
            suggestions = self.get_chatgpt_suggestions(star_rating, product_name, review_tone,meta_info)
            # print(type(suggestions))
            return Response(suggestions, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


    def get_chatgpt_suggestions(self, star_rating,product_name,review_tone,meta_info):
        openai.api_key = settings.OPEN_API_KEY
        RESPONSE_JSON = {
            "suggestions":["word1","word2","word3","word4", "word5, word6", "word7","word8","word9"]
        }
        prompt = f"""User gives {star_rating} out of 5 stars to {product_name} and about product you can get from meta_info here {meta_info}. Generate 9-11 describing words or phrases in a {review_tone} tone according to the star rated.
        Replace the words in an array with the actual words.
        
        RESPONSE_JSON : {RESPONSE_JSON}
        
        Make sure to format your response like RESPONSE_JSON and use it as a guide.
        
        Return the response in json format only."""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a helpful assistant for reviewing products/services/business/website."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=60
        )

        

        suggestions = response['choices'][0]['message']['content'].strip()
        try:
            json_response = json.loads(suggestions)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {e}")
            json_response = {}
        # print(suggestions)
        
        # suggestions = suggestions.strip('[]')
        # suggestions = [s.strip('"').strip("'") for s in suggestions.split(", ")]
        # suggestions = json.loads(suggestions)
        # return suggestions
        # suggestions = suggestions.strip("[]").replace('\n', '').replace('"', '').replace("'", "")
        # suggestions = [s.strip() for s in suggestions.split(",")]
        return json_response


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
            meta_info = request.data['meta_info']
            review = self.get_chatgpt_review(star_rating, user_selected_words, product_name,meta_info)
            return Response({'AIreview': review}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

    def get_chatgpt_review(self, star_rating, user_selected_words, product_name,meta_info):
        openai.api_key = settings.OPEN_API_KEY
        prompt = f"User gave {star_rating} out of 5 stars and selected '{user_selected_words}' as the best describing words for {product_name}. Provide a detailed 80-100 words review based on these criteria for {product_name} and meta description of that is {meta_info} provided, in easy real language. Ignore description."
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for reviewing products/services/business/website."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )
        review = response['choices'][0]['message']['content']
        return review
      
