from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from .models import ProductReviews, ReviewSettings
from .serializers import ProductReviewsSerializer, CustomerSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotFound
from django.db.models import Avg
import logging
import json 
from django.http import JsonResponse

logger = logging.getLogger('review_system')
logger.setLevel(logging.DEBUG)

class ProductReviewsListAPI(APIView):
    # permission_classes = [IsAuthenticated]
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
            reviews = ProductReviews.objects.filter(domain=domain, status='approve')
            if product_name:
                reviews = reviews.filter(product_name=product_name)

            total_product_reviews = reviews.filter(product_name__isnull=False).count()
            total_business_reviews = reviews.filter(product_name__isnull=True).count()
            
            if not reviews.exists():
                return Response(
                    {
                        "status": status.HTTP_204_NO_CONTENT,
                        "message": "No approved Reviews Found.",
                        "data": []
                    },
                    status=status.HTTP_204_NO_CONTENT,
                )
            
            reviews = reviews.order_by("-created_at")
            # Calculate average star rating for business and product reviews separately
            business_reviews = reviews.filter(product_name__isnull=True)
            business_average_star_rating = business_reviews.aggregate(avg_star_rating=Avg('star_rating'))['avg_star_rating'] or 0.0
            business_average_star_rating = round(business_average_star_rating, 1)

            product_reviews = reviews.filter(product_name__isnull=False)
            product_average_star_rating = product_reviews.aggregate(avg_star_rating=Avg('star_rating'))['avg_star_rating'] or 0.0
            product_average_star_rating = round(product_average_star_rating, 1)

            reviews_data = {'business': [], 'product': []}


            for review in reviews:
                    review_dict = review.to_dict()
                    review_dict['reply_created_at'] = review.reply_created_at
                    review_dict['reply_text'] = review.reply_text
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
                            "total_business_reviews": total_business_reviews,
                            "business_reviews": reviews_data['business'],
                        },
                        "product": {
                            "average_star_rating": product_average_star_rating,
                            "total_product_reviews": total_product_reviews,
                            "product_reviews": reviews_data['product'],
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
            serializer = ProductReviewsSerializer(data=new_data)

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
                        "data": ProductReviewsSerializer(review_instance).data,
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

            customer_data['domain_name'] = parsed_data.get('domain_name', None)

            if 'contact' in parsed_data and parsed_data['contact'].get('email'):
                customer_data['email'] = parsed_data['contact']['email']

            if 'plan_title' in parsed_data and parsed_data['plan_title']:
                customer_data['plan_name'] = parsed_data['plan_title']

            if 'plan_start_date' in parsed_data and parsed_data['plan_start_date']:
                start_date = datetime.strptime(parsed_data['plan_start_date'], "%d/%m/%y").strftime("%Y-%m-%d")
                customer_data['date_start'] = start_date

                if 'plan_cycle_duration' in parsed_data:
                    if parsed_data['plan_cycle_duration'] == "1 month":
                        end_date = (datetime.strptime(parsed_data['plan_start_date'], "%d/%m/%y") + timedelta(days=30)).strftime("%Y-%m-%d")
                    elif parsed_data['plan_cycle_duration'] == "1 year":
                        end_date = (datetime.strptime(parsed_data['plan_start_date'], "%d/%m/%y") + timedelta(days=365)).strftime("%Y-%m-%d")
                    else:
                        end_date = parsed_data.get('plan_valid_until', 'Until canceled')
                    customer_data['date_end'] = end_date
                else:
                    customer_data['date_end'] = parsed_data.get('plan_valid_until', 'Until canceled')

            if 'plan_price' in parsed_data and parsed_data['plan_price'].get('value'):
                customer_data['plan_price'] = parsed_data['plan_price']['value']

            customer_data['first_name'] = parsed_data.get('name', {}).get('first', None)
            customer_data['last_name'] = parsed_data.get('name', {}).get('last', None)

            customer_data['password'] = None
            

            # Validate and save the customer data
            serializer = CustomerSerializer(data=customer_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            customer_logger.error(f"Error processing data: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
   