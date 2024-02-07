from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ProductReviews
from .serializers import ProductReviewsSerializer
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User


class ProductReviewsListAPI(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    def get(self, request):
        product_id = request.query_params.get('product_id')
        # product_id = request.data.get('product_id')

        try:
            if not product_id:
                return Response(
                    {
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": "Missing product_id in query parameters",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user_id = request.user.id
            if not user_id:
                reviews = ProductReviews.objects.filter(product_id=product_id)
            else:
                reviews = ProductReviews.objects.filter(product_id=product_id, user_id=user_id)

            if not reviews.exists():
                return Response(
                    {
                        "status": status.HTTP_404_NOT_FOUND,
                        "message": "No reviews found for the specified product_id.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = ProductReviewsSerializer(reviews, many=True)
            return Response(
                {
                    "status": status.HTTP_200_OK,
                    "message": "Product reviews retrieved successfully!",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": f"Error while retrieving product reviews: {str(e)}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def post(self, request):
        try:
            product_id = request.data.get('product_id')

            if not product_id:
                return Response(
                    {
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": "Missing product_id in request data",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            

            request.data['user'] = request.user.id
            serializer = ProductReviewsSerializer(data=request.data)
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

            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Error in data validation",
                    "data": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": f"Error while posting product review: {str(e)}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class ProductReviewsDetailAPI(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    def put(self, request, pk):
        try:
            review = ProductReviews.objects.get(pk=pk)
            request.data['user'] = request.user.id
            serializer = ProductReviewsSerializer(review, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status": status.HTTP_200_OK,
                        "message": "Product review updated successfully!",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Error in data validation",
                    "data": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ProductReviews.DoesNotExist:
            return Response(
                {
                    "status": status.HTTP_404_NOT_FOUND,
                    "message": "Product review not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": f"Error while updating product review: {str(e)}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, pk):
        try:
            review = ProductReviews.objects.get(pk=pk)
            review.delete()
            return Response(
                {
                    "status": status.HTTP_200_OK,
                    "message": "Product review deleted successfully!",
                },
                status=status.HTTP_200_OK,
            )
        except ProductReviews.DoesNotExist:
            return Response(
                {
                    "status": status.HTTP_404_NOT_FOUND,
                    "message": "Product review not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": f"Error while deleting product review: {str(e)}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
