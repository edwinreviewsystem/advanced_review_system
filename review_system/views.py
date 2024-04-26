from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ProductReviews
from .serializers import ProductReviewsSerializer
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotFound
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework.exceptions import ValidationError
from django.db.models import Q, Count


class ProductReviewsListAPI(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    def get(self, request):
        product_name = request.query_params.get('product_name')
        domain = request.query_params.get('domain')

        try:
            if not (product_name or domain):
                return Response(
                    {
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": "Missing product_name/domain in query parameters",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user_id = request.user.id

            data = {'business': [], 'product': []}
            reviews = ProductReviews.objects.filter(domain=domain)
            if product_name:
                reviews = reviews.filter(product_name=product_name)
            
            if not reviews.exists():
                return Response(
                    {
                        "status": status.HTTP_204_NO_CONTENT,
                        "message": "No reviews found.",
                        "data": []
                    },
                    status=status.HTTP_204_NO_CONTENT,
                )
            data['product'] = [review.to_dict() for review in reviews if review.product_name]
            data['business'] = [review.to_dict() for review in reviews if not review.product_name]   

            # serializer = ProductReviewsSerializer(reviews, many=True)
            return Response(
                {
                    "status": status.HTTP_200_OK,
                    "message": "Product reviews retrieved successfully!",
                    "data": data,
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
            star_rating = request.data.get('star_rating')
            name = request.data.get('name')
            email = request.data.get('email')
            # product_name = request.data.get('product_name')
            domain = request.data.get('domain')
            review = request.data.get('review')
            image = request.FILES.get('image')

            new_data = {
                #  'product_name': product_name,
                 'domain':domain,
                 'star_rating': star_rating,
                 'email':email,
                 'name': name,
                 'review': review,
                 'image':image,
            }

      
            # request.data['user'] = request.user.id
            new_data['image'] = image if image else None
            serializer = ProductReviewsSerializer(data=new_data)
         
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status": status.HTTP_201_CREATED,
                        "message": "New Review added!",
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
                    "message": f"Error while posting Review: {str(e)}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
    def get_review_count_by_domain(self):
        # This method can be used to get the count of reviews for each domain
        domain_review_counts = ProductReviews.objects.values('domain').annotate(count=Count('id'))
        return domain_review_counts


class ProductReviewsDetailAPI(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    def put(self, request, pk):
        try:
            review = ProductReviews.objects.get(pk=pk)
            print('put product pk=',pk)
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
            raise NotFound()
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
                    "status": status.HTTP_204_NO_CONTENT,
                    "message": "Product review deleted successfully!",
                },
                status=status.HTTP_204_NO_CONTENT,
            )
        except ProductReviews.DoesNotExist:
            raise NotFound()
        except Exception as e:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": f"Error while deleting product review: {str(e)}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
