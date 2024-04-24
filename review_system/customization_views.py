from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny 
from rest_framework import status

from .models import *
from .serializers import *

class ReviewFormDesignListAPI(APIView):
    # permission_classes = [IsAuthenticated]  
    permission_classes = [AllowAny]

    def get(self, request):
        designs = ReviewFormDesign.objects.all()   # Fetch all reviewdesign elements
        serializer = ReviewFormDesignSerializer(designs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        try:
            design = ReviewFormDesign.objects.get(pk=pk)  # Fetch specific reviewdesign element
            serializer = ReviewFormDesignSerializer(design, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ReviewFormDesign.DoesNotExist:
            return Response({'error': 'Review form design not found'}, status=status.HTTP_404_NOT_FOUND)

class ReviewListDesignListAPI(APIView):
    # permission_classes = [IsAuthenticated]  
    permission_classes = [AllowAny]  

    def get(self, request):
        designs = ReviewListDesign.objects.all()  
        serializer = ReviewListDesignSerializer(designs, many=True)  
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        try:
            design = ReviewListDesign.objects.get(pk=pk)  
            serializer = ReviewListDesignSerializer(design, data=request.data) 
            if serializer.is_valid():
                serializer.save()  # Save the updated design element
                return Response(serializer.data, status=status.HTTP_200_OK)  
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
        except ReviewListDesign.DoesNotExist:
            return Response({'error': 'Review list design not found'}, status=status.HTTP_404_NOT_FOUND)  
