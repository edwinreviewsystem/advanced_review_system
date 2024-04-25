from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ReviewFormDesign, ReviewListDesign
from .serializers import ReviewFormDesignSerializer, ReviewListDesignSerializer

class CustomizationAPIView(APIView):
    def get(self, request):
        review_form_settings = ReviewFormDesign.objects.all()
        review_list_settings = ReviewListDesign.objects.all()

        review_form_serializer = ReviewFormDesignSerializer(review_form_settings, many=True)
        review_list_serializer = ReviewListDesignSerializer(review_list_settings, many=True)

        return Response({
            'review_form': review_form_serializer.data,
            'review_design': review_list_serializer.data
        })
