from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.exceptions import NotFound
from .models import ReviewTone
from .serializers import ReviewToneSerializer

class ReviewToneListAPIView(APIView):

    def get(self, request):
        # if pk:  
        #     try:
        #         review_tone = ReviewTone.objects.get(pk=pk)
        #         serializer = ReviewToneSerializer(review_tone)
        #         return Response(serializer.data)
        #     except ReviewTone.DoesNotExist:
        #         raise NotFound()
        # else:  
        try:
            review_tones = ReviewTone.objects.all().order_by('name')
            serializer = ReviewToneSerializer(review_tones, many=True)
            return Response(
                {
                    "status": status.HTTP_200_OK,
                    "message": "Review tone Retrieved successfully!",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": f"Error in Retrieving Review Tones: {str(e)}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


    def post(self, request):
        serializer = ReviewToneSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                    {
                        "status": status.HTTP_201_CREATED,
                        "message": "Product review added!",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReviewToneDetailAPIView(APIView):

    def put(self, request, pk):
        try:
            review_tone = ReviewTone.objects.get(pk=pk)
        except ReviewTone.DoesNotExist:
            raise NotFound()

        serializer = ReviewToneSerializer(review_tone, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                    {
                        "status": status.HTTP_200_OK,
                        "message": "Review tone Updated successfully!",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    def delete(self, request, pk):
        try:
            review_tone = ReviewTone.objects.get(pk=pk)
            review_tone.delete()
            return Response(
                {
                    "status": status.HTTP_204_NO_CONTENT,
                    "message": "Review tone Deleted successfully!",
                },
                status=status.HTTP_204_NO_CONTENT,
            )
        except ReviewTone.DoesNotExist:
            raise NotFound()
