from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ReviewFormDesign, ReviewListDesign
from .serializers import ReviewFormDesignSerializer, ReviewListDesignSerializer
from rest_framework import status

class CustomizationAPIView(APIView):
    def get(self, request):
        domain = request.query_params.get('domain')
        # if not domain:
        #     return Response({'error': 'Pass domain in the query parameters to get customization'}, status=status.HTTP_400_BAD_REQUEST)
        
        response_data = {'domain': domain}
        try:
            review_form_settings = ReviewFormDesign.objects.get(domain=domain)
            review_form_data = ReviewFormDesignSerializer(review_form_settings).data
            response_data['review_form'] = review_form_data
        except ReviewFormDesign.DoesNotExist:
            pass

        try:
            review_list_settings = ReviewListDesign.objects.get(domain=domain)
            review_list_data = ReviewListDesignSerializer(review_list_settings).data
            response_data['review_design'] = review_list_data
        except ReviewListDesign.DoesNotExist:
            pass

        if 'review_form' in response_data or 'review_design' in response_data:
            return Response(response_data)
        else:
            return Response({'error': f'No customize CSS settings found for domain - {domain}'}, status=status.HTTP_204_NO_CONTENT)
        



# class CustomizationAPIView(APIView):
#     def get(self, request):
#         domain = request.query_params.get('domain_name')
#         try:
#             review_form_settings = ReviewFormDesign.objects.get(domain_name=domain)
#             review_list_settings = ReviewListDesign.objects.get(domain_name=domain)

#             review_form_serializer = ReviewFormDesignSerializer(review_form_settings)
#             review_list_serializer = ReviewListDesignSerializer(review_list_settings)

#             return Response({
#                 'domain': domain,
#                 'review_form': review_form_serializer.data,
#                 'review_design': review_list_serializer.data
#             })

#         except ReviewFormDesign.DoesNotExist:
#             return Response({
#                 'error': f'ReviewFormDesign settings not found for domain {domain}'
#             }, status=status.HTTP_204_NO_CONTENT)

#         except ReviewListDesign.DoesNotExist:
#             return Response({
#                 'error': f'ReviewListDesign settings not found for domain {domain}'
#             }, status=status.HTTP_204_NO_CONTENT)
        