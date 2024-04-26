# from rest_framework.views import APIView
# from rest_framework.response import Response
# from .models import ReviewFormDesign, ReviewListDesign
# from .serializers import ReviewFormDesignSerializer, ReviewListDesignSerializer

# class CustomizationAPIView(APIView):
#     def get(self, request):
#         review_form_settings = ReviewFormDesign.objects.all()
#         review_list_settings = ReviewListDesign.objects.all()

#         review_form_serializer = ReviewFormDesignSerializer(review_form_settings, many=True)
#         review_list_serializer = ReviewListDesignSerializer(review_list_settings, many=True)

#         return Response({
#             'review_form': review_form_serializer.data,
#             'review_design': review_list_serializer.data
#         })


from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ReviewFormDesign, ReviewListDesign
from .serializers import ReviewFormDesignSerializer, ReviewListDesignSerializer
from rest_framework import status

class CustomizationAPIView(APIView):
    def get(self, request, domain):
        try:
            review_form_settings = ReviewFormDesign.objects.get(domain_name=domain)
            review_list_settings = ReviewListDesign.objects.get(domain_name=domain)

            review_form_serializer = ReviewFormDesignSerializer(review_form_settings)
            review_list_serializer = ReviewListDesignSerializer(review_list_settings)

            return Response({
                'domain': domain,
                'review_form': review_form_serializer.data,
                'review_design': review_list_serializer.data
            })

        except ReviewFormDesign.DoesNotExist:
            return Response({
                'error': f'ReviewFormDesign settings not found for domain {domain}'
            }, status=status.HTTP_204_NO_CONTENT)

        except ReviewListDesign.DoesNotExist:
            return Response({
                'error': f'ReviewListDesign settings not found for domain {domain}'
            }, status=status.HTTP_204_NO_CONTENT)

