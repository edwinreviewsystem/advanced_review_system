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
from django.db.models import Avg


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


            reviews = ProductReviews.objects.filter(domain=domain, status='approve')
            if product_name:
                reviews = reviews.filter(product_name=product_name)
            
            if not reviews.exists():
                return Response(
                    {
                        "status": status.HTTP_204_NO_CONTENT,
                        "message": "No approved Reviews Found.",
                        "data": []
                    },
                    status=status.HTTP_204_NO_CONTENT,
                )
            
            
            # Calculate average star rating for business and product reviews separately
            business_reviews = reviews.filter(product_name__isnull=True)
            business_average_star_rating = business_reviews.aggregate(avg_star_rating=Avg('star_rating'))['avg_star_rating'] or 0.0

            product_reviews = reviews.filter(product_name__isnull=False)
            product_average_star_rating = product_reviews.aggregate(avg_star_rating=Avg('star_rating'))['avg_star_rating'] or 0.0
            reviews_data = {'business': [], 'product': []}


            for review in reviews:
                    review_dict = review.to_dict()
                    if review.product_name:
                        reviews_data['product'].append(review_dict)
                    else:
                        reviews_data['business'].append(review_dict)  


            return Response(
                {
                    "status": status.HTTP_200_OK,
                    "message": "Reviews Retrieved successfully!",
                    "data": {
                        "business": {
                            "average_star_rating": business_average_star_rating,
                            "business reviews": reviews_data['business'],
                        },
                        "product": {
                            "average_star_rating": product_average_star_rating,
                            "product reviews": reviews_data['product'],
                        },
                    },
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": f"Error while retrieving Reviews: {str(e)}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def post(self, request):
        try:
            star_rating = request.data.get('star_rating')
            name = request.data.get('name')
            email = request.data.get('email')
            product_name = request.data.get('product_name')
            domain = request.data.get('domain')
            review = request.data.get('review')
            image = request.FILES.get('image')

            new_data = {
                 'product_name': product_name,
                 'domain':domain,
                 'star_rating': star_rating,
                 'email':email,
                 'name': name,
                 'review': review,
                 'image':image,
            }

             # Check if auto-approval is enabled
            # if request.user and isinstance(request.user, User) and request.user.is_superuser and request.user.auto_approve_reviews:
            #     new_data['status'] = 'approve'
            # else:
            #     new_data['status'] = 'approve'


            # Auto-approve all reviews
                # ProductReviews.objects.filter(status='pending').update(status='approve')


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
                    "message": f"Error while posting new Review: {str(e)}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
    def get_review_count_by_domain(self):
        domain_review_counts = ProductReviews.objects.values('domain').annotate(count=Count('id'))
        return domain_review_counts


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
                        "message": "Review Updated successfully!",
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
                    "message": f"Error while updating Review: {str(e)}",
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
                    "message": "Review deleted successfully!",
                },
                status=status.HTTP_204_NO_CONTENT,
            )
        except ProductReviews.DoesNotExist:
            raise NotFound()
        except Exception as e:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": f"Error while deleting Review: {str(e)}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
