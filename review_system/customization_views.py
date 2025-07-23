from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ReviewFormDesign, ReviewListDesign, Sites
from .serializers import ReviewFormDesignSerializer, ReviewListDesignSerializer
from rest_framework import status

class CustomizationAPIView(APIView):
    def get(self, request):
        domain = request.query_params.get('domain')
        if not domain:
            return Response(
                {'error': 'Pass domain in the query parameters to get customization'},
                status=status.HTTP_400_BAD_REQUEST
            )

        response_data = {'domain': domain, 'review_form': {}, 'review_design': {}}

        try:
            site = Sites.objects.get(domain=domain)
        except Sites.DoesNotExist:
            return Response(
                {'error': f"No site found with domain: {domain}"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            review_form_settings = ReviewFormDesign.objects.get(site=site)
            review_form_data = ReviewFormDesignSerializer(review_form_settings).data
            response_data['review_form'] = review_form_data
        except ReviewFormDesign.DoesNotExist:
            pass

        try:
            review_list_settings = ReviewListDesign.objects.get(site=site)
            review_list_data = ReviewListDesignSerializer(review_list_settings).data
            response_data['review_design'] = review_list_data
        except ReviewListDesign.DoesNotExist:
            pass

        if response_data['review_form'] or response_data['review_design']:
            return Response(response_data)
        else:
            return Response(
                {'error': f'No customization settings found for domain - {domain}'},
                status=status.HTTP_204_NO_CONTENT
            )
        
