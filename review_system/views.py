from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotFound
from django.db.models import Avg
import logging
import json 
from django.http import JsonResponse

logger = logging.getLogger('review_system')
logger.setLevel(logging.DEBUG)

class ProductReviewsListAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        product_name = request.query_params.get('product_name')
        domain = request.query_params.get('domain')

        if not (product_name or domain):
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Missing product_name/domain in query parameters",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Fetch Product Reviews (reviews with product_name)
            product_reviews = ProductReviews.objects.filter(domain=domain, status='approve', product_name__isnull=False)
            if product_name:
                product_reviews = product_reviews.filter(product_name=product_name)

            # Fetch Business Reviews (reviews without product_name)
            business_reviews = ProductReviews.objects.filter(domain=domain, status='approve', product_name__isnull=True)

            # Fetch Google Reviews
            google_reviews = Google_Reviews.objects.filter(domain_name=domain, status='approve')

            # Calculate total and average star ratings
            total_product_reviews = product_reviews.count()
            total_business_reviews = business_reviews.count()

            product_average_star_rating = product_reviews.aggregate(avg_star_rating=Avg('star_rating'))['avg_star_rating'] or 0.0
            product_average_star_rating = round(product_average_star_rating, 1)

            business_average_star_rating = business_reviews.aggregate(avg_star_rating=Avg('star_rating'))['avg_star_rating'] or 0.0
            business_average_star_rating = round(business_average_star_rating, 1)

            # Serialize data for each type of review
            product_reviews_data = ReviewSerializer(product_reviews, many=True).data
            business_reviews_data = ReviewSerializer(business_reviews, many=True).data
            google_reviews_data = ReviewSerializer(google_reviews, many=True).data

            return Response(
                {
                    "status": status.HTTP_200_OK,
                    "message": "Reviews Retrieved successfully!",
                    "data": {
                        "business": {
                            "average_star_rating": business_average_star_rating,
                            "total_business_reviews": total_business_reviews,
                            "business_reviews": business_reviews_data,
                        },
                        "product": {
                            "average_star_rating": product_average_star_rating,
                            "total_product_reviews": total_product_reviews,
                            "product_reviews": product_reviews_data,
                        },
                        "google": {
                            "total_google_reviews": len(google_reviews_data),
                            "google_reviews": google_reviews_data,
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
            source = request.data.get('source')

            new_data = {
                 'product_name': product_name,
                 'domain':domain,
                 'star_rating': star_rating,
                 'email':email,
                 'name': name,
                 'review': review,
                 'image':image if image else None,
                 'source':source
            }

            # new_data['image'] = image if image else None
            serializer = ReviewSerializer(data=new_data)

            # Fetch the ReviewSettings for the given domain
            settings = ReviewSettings.objects.filter(domain=domain).first()
            auto_approve = settings.auto_approve if settings else False 
            # print(f'auto_approve value for {domain} is {auto_approve}')
         
            if serializer.is_valid():
                status_value = ProductReviews.APPROVE if auto_approve else ProductReviews.PENDING
                serializer.validated_data['status'] = status_value

                review_instance = serializer.save()
                # ProductReviews.objects.filter(domain=domain).update(status=status_value)
                return Response(
                    {
                        "status": status.HTTP_201_CREATED,
                        "message": "New Review added!",
                        "data":ReviewSerializer(review_instance).data,
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


customer_logger = logging.getLogger('customer_create_logger')


class CustomerCreateAPIView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            
            if isinstance(request.data, dict):
                parsed_data = request.data
            else:
                try:
                    parsed_data = json.loads(request.body.decode('utf-8'))
                except json.JSONDecodeError:
                    return JsonResponse({"error": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)

            parsed_data = parsed_data.get('data', {})
            customer_logger.debug(f"Incoming data: {parsed_data}")

            customer_data = {}

            
            customer_data['email'] = parsed_data.get('contact', {}).get('email')
            if not customer_data['email']:
                return JsonResponse({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

            
            customer_data['plan_name'] = parsed_data.get('plan_title')
            if not customer_data['plan_name']:
                return JsonResponse({"error": "Plan name is required"}, status=status.HTTP_400_BAD_REQUEST)

            
            customer_data['plan_price'] = parsed_data.get('plan_price', {}).get('value')
            if not customer_data['plan_price']:
                return JsonResponse({"error": "Plan price is required"}, status=status.HTTP_400_BAD_REQUEST)

            
            start_date = datetime.now().date()
            if 'plan_start_date' in parsed_data and parsed_data['plan_start_date']:
                start_date = datetime.strptime(parsed_data['plan_start_date'], "%d/%m/%y").date()

            customer_data['date_start'] = start_date.strftime("%Y-%m-%d")

            
            end_date = None
            if 'plan_cycle_duration' in parsed_data:
                duration = parsed_data['plan_cycle_duration']
                if 'day' in duration:
                    days = int(duration.split()[0])
                    end_date = start_date + timedelta(days=days)
                elif 'week' in duration:
                    weeks = int(duration.split()[0])
                    end_date = start_date + timedelta(weeks=weeks)
                elif 'month' in duration:
                    months = int(duration.split()[0])
                    end_date = start_date + relativedelta(months=months)
                elif 'year' in duration:
                    years = int(duration.split()[0])
                    end_date = start_date + relativedelta(years=years)

                if end_date:
                    customer_data['date_end'] = end_date.strftime("%Y-%m-%d")
                else:
                    customer_data['date_end'] = 'Until canceled'
            else:
                customer_data['date_end'] = 'Until canceled'

            customer_data['first_name'] = parsed_data.get('name', {}).get('first', None)
            customer_data['last_name'] = parsed_data.get('name', {}).get('last', None)
            customer_data['password'] = None

            
            serializer = CustomerSerializer(data=customer_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            customer_logger.error(f"Error processing data: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

