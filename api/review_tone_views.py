from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework import status
from rest_framework.exceptions import NotFound
from .models import ReviewTone
from .serializers import ReviewToneSerializer

from django.contrib.auth.decorators import user_passes_test

def admin_only(function):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return function(request, *args, **kwargs)
        else:
            return Response(
                {
                    "status": status.HTTP_401_UNAUTHORIZED,
                    "message": "User Authentication Required.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

    return wrapper


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
            review_tones = ReviewTone.objects.all()
            if not review_tones.exists():
                return Response(
                    {
                        "status": status.HTTP_200_OK,
                        "message": "No review tones found in database.",
                        "data": [],
                    },
                    status=status.HTTP_200_OK,
                )
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
        

class ReviewToneCreateAPIView(APIView):
    # permission_classes = [IsAdminUser]
    # @admin_only
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
    # permission_classes = [IsAdminUser]
   
    # @admin_only
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

    # @admin_only
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
