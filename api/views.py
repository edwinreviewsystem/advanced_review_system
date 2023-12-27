from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import ProductReviewSerializer
import openai
from django.conf import settings
from django.views.generic import TemplateView

class HomePageView(TemplateView):
    template_name = 'home.html'

class GetChatGPTSuggestions(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ProductReviewSerializer(data=request.data)
        if serializer.is_valid():
            star_rating = serializer.validated_data['star_rating']
            product_name = serializer.validated_data['product_name']
            suggestions = self.get_chatgpt_suggestions(star_rating,product_name)                                                                                                                                                                                                                                                                                                                                                                        

            if 'error' in suggestions:
                return Response({'error': suggestions}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'suggestions': suggestions})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_chatgpt_suggestions(self, star_rating,product_name):
        try:
            openai.api_key = settings.OPEN_API_KEY
            prompt = f"User rated the product{product_name} {star_rating}stars. Generate 5-8 best describing words for {star_rating} of {product_name}.Ignore description."

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for the product review system."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=60
            )

            suggestions = response['choices'][0]['message']['content']
            suggestions_list = [word.split(". ")[1] for word in suggestions.split("\n") if word.strip()]

            # suggestions = "Neutral, average, satisfactory, acceptable, standard, decent, usual"
            return  suggestions_list 
        except Exception as e:
            return str(e)


class GetChatGPTReview(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ProductReviewSerializer(data=request.data)
        if serializer.is_valid():
            star_rating = serializer.validated_data['star_rating']
            user_word = serializer.validated_data['user_word']
            product_name = serializer.validated_data['product_name']
            review = self.get_chatgpt_review(star_rating, user_word,product_name)

            if 'error' in review:
                return Response({'error': review}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'review': review})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_chatgpt_review(self, star_rating, user_word, product_name):
        try:
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
        except Exception as e:
            return str(e)
