# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from .serializers import AIReviewSerializer
# import openai
# from django.conf import settings


# class GetChatGPTSuggestions(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         try:
#             serializer = AIReviewSerializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             star_rating = serializer.validated_data['star_rating']
#             product_name = serializer.validated_data['product_name']
#             review_tone = serializer.validated_data['review_tone']
#             language = request.data.get('language', 'english')  

#             suggestions = self.get_chatgpt_suggestions(star_rating, product_name, review_tone, language)
#             return Response({'suggestions': suggestions}, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

#     def get_chatgpt_suggestions(self, star_rating, product_name, review_tone, language):
#         openai.api_key = settings.OPEN_API_KEY
#         prompt = (f"User gives {star_rating} stars to {product_name}. Generate 9-11 best describing words in a {review_tone} tone, "
#               f"in {language}. Ignore description and provide the words in an array format.")

#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant for reviewing products/services."},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=60
#         )

#         suggestions = response['choices'][0]['message']['content'].strip()
#         suggestions = suggestions.strip('[]')
#         suggestions = [s.strip('"').strip("'") for s in suggestions.split(", ")]
#         return suggestions
       
# class GetChatGPTReview(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         try:
#             serializer = AIReviewSerializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
            
#             star_rating = serializer.validated_data['star_rating']
#             user_selected_words = serializer.validated_data['user_selected_words']
#             product_name = serializer.validated_data['product_name']
#             language = request.data.get('language', 'english') 
            
#             review = self.get_chatgpt_review(star_rating, user_selected_words, product_name, language)
#             return Response({'AIreview': review}, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

#     def get_chatgpt_review(self, star_rating, user_selected_words, product_name, language):
#         openai.api_key = settings.OPEN_API_KEY
#         prompt = (f"User gives {star_rating} stars and selected {user_selected_words} as the best describing words for {product_name}. "
#                   f"Provide a detailed 80-100 words review on this basis for {product_name}, in {language}. Ignore description.")
        
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant for reviewing products/services."},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=200
#         )
#         review = response['choices'][0]['message']['content']
#         return review
