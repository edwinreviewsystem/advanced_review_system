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
from django.utils import timezone 

logger = logging.getLogger('review_system')
logger.setLevel(logging.DEBUG)

class ProductReviewsListAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        domain = request.query_params.get('domain')

        if not domain:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Missing domain in query parameters",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Step 1: Find Site by domain
            site = Sites.objects.filter(domain=domain).first()
            if not site:
                return Response(
                    {"status": status.HTTP_404_NOT_FOUND, "message": "Site not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Step 2: Get active PlanSubscription for that site
            plan_subscription = PlanSubscription.objects.filter(
                site=site,
                status='active'
            ).select_related('plan').first()

            if not plan_subscription or not plan_subscription.plan:
                return Response(
                    {"status": status.HTTP_404_NOT_FOUND, "message": "No active plan subscription found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            plan = plan_subscription.plan
            plan_id = plan.id
            print("Plan ID:", plan_id)
            is_trial = plan_subscription.is_trial
            trial_ends_at = plan_subscription.trial_ends_at
            today = timezone.now().date()

            business_reviews_qs = ProductReviews.objects.filter(
                site=site,
                status="approve",
                product_name__isnull=True
            ).order_by("-created_at")

            # Flag to decide if we include product + google reviews
            include_product_google = False

            # Step 4: Apply plan logic
            if plan_id == 1:  # Freemium
                if is_trial and (not trial_ends_at or today <= trial_ends_at):
                    print("In is trial")
                    # Active trial → show everything
                    include_product_google = True
                else:
                    print("Out is trial")
                    # Trial expired → limit all reviews to 6
                    business_reviews_qs = business_reviews_qs[:6]
                    include_product_google = True  # Still show product + google (but limited below)
            else:
                # Premium plan
                include_product_google = True

            # Step 5: Business reviews
            total_business_reviews = business_reviews_qs.count()
            business_avg_rating = business_reviews_qs.aggregate(
                avg_star_rating=Avg('star_rating')
            )['avg_star_rating'] or 0.0
            business_avg_rating = round(business_avg_rating, 1)
            business_reviews_data = ReviewSerializer(business_reviews_qs, many=True).data

            response_data = {
                "business": {
                    "average_star_rating": business_avg_rating,
                    "total_business_reviews": total_business_reviews,
                    "business_reviews": business_reviews_data,
                }
            }

            # Step 6: Product + Google reviews (if allowed)
            if include_product_google:
                product_reviews_qs = ProductReviews.objects.filter(
                    site=site,
                    status="approve",
                    product_name__isnull=False
                ).order_by("-created_at")

                google_reviews_qs = Google_Reviews.objects.filter(
                    site=site
                ).order_by("-created_at")

                # If freemium trial expired → limit to 6 each
                if plan_id == 1 and (not is_trial or (trial_ends_at and today > trial_ends_at)):
                    product_reviews_qs = product_reviews_qs[:6]
                    google_reviews_qs = google_reviews_qs[:6]

                # Product Reviews
                total_product_reviews = product_reviews_qs.count()
                product_avg_rating = product_reviews_qs.aggregate(
                    avg_star_rating=Avg('star_rating')
                )['avg_star_rating'] or 0.0
                product_avg_rating = round(product_avg_rating, 1)
                product_reviews_data = ReviewSerializer(product_reviews_qs, many=True).data

                # Google Reviews
                total_google_reviews = google_reviews_qs.count()
                google_avg_rating = google_reviews_qs.aggregate(
                    avg_star_rating=Avg('rating')
                )['avg_star_rating'] or 0.0
                google_avg_rating = round(google_avg_rating, 1)
                google_reviews_data = ReviewSerializer(google_reviews_qs, many=True).data

                response_data.update({
                    "product": {
                        "average_star_rating": product_avg_rating,
                        "total_product_reviews": total_product_reviews,
                        "product_reviews": product_reviews_data,
                    },
                    "google": {
                        "average_star_rating": google_avg_rating,
                        "total_google_reviews": total_google_reviews,
                        "google_reviews": google_reviews_data,
                    }
                })

            return Response(
                {
                    "status": status.HTTP_200_OK,
                    "message": "Reviews retrieved successfully!",
                    "data": response_data,
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {
                    "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "message": f"Error while retrieving reviews: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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

            # --- Step 1: Fetch Site using domain ---
            site = Sites.objects.filter(domain=domain).first()
            if not site:
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": f"No site found with domain '{domain}'",
                }, status=status.HTTP_400_BAD_REQUEST)

            # --- Step 2: Fetch active PlanSubscription to get plan_id ---
            plan_subscription = PlanSubscription.objects.filter(site=site, status="active").select_related('plan').first()
            plan_id = plan_subscription.plan.id if plan_subscription and plan_subscription.plan else None

            # --- Step 3: Load Review Settings ---
            settings = ReviewSettings.objects.filter(domain=domain).first()
            auto_approve = settings.auto_approve if settings and settings.auto_approve is not None else True

            # --- Step 4: Prepare serializer input data ---
            new_data = {
                'product_name': product_name,
                'domain': domain,
                'star_rating': star_rating,
                'email': email,
                'name': name,
                'review': review,
                'image': image if image else None,
                'source': source
            }

            serializer = ReviewSerializer(data=new_data)

            if serializer.is_valid():
                # Determine status based on plan
                status_value = ProductReviews.APPROVE if auto_approve else ProductReviews.PENDING

                if plan_id == 1:  # Freemium plan
                    total_reviews = ProductReviews.objects.filter(site=site).count()
                    if total_reviews >= 6:
                        status_value = ProductReviews.PENDING  # Limit reviews

                # Save review with status and site foreign key
                serializer.validated_data['status'] = status_value
                review_instance = ProductReviews.objects.create(
                    **serializer.validated_data,
                    site=site
                )

                return Response({
                    "status": status.HTTP_201_CREATED,
                    "message": "New Review added!",
                    "data": ReviewSerializer(review_instance).data,
                }, status=status.HTTP_201_CREATED)

            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Error in data validation",
                "data": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": f"Error while posting new Review: {str(e)}",
            }, status=status.HTTP_400_BAD_REQUEST)


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

