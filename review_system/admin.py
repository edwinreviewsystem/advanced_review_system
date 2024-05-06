from django.contrib import admin
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from .models import *
from django.utils.html import format_html
from django.db.models import F
from sorl.thumbnail import get_thumbnail
from django.conf import settings
from django.template.loader import render_to_string


class ProductReviewsListAdmin(admin.ModelAdmin):
    list_display = ('id', 'review_one_line', 'star_rating', 'name', 'email',  'domain', 'display_image', 'status', 'created_at')
    list_display_links = ('id', 'domain')
    search_fields = ('name', 'email', 'domain', 'status')
    list_filter = ('created_at','domain','status')
    list_per_page = 20

    actions = ['auto_approve_reviews', 'auto_disapprove_reviews']
    
    
    def display_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="70px" height="60px" />'.format(obj.image.url)
            )
    display_image.short_description = "Uploaded Image"

    def review_one_line(self, obj):
        return obj.review[:22] + '..' if len(obj.review) > 22 else obj.review
    review_one_line.short_description = 'Review'

    def auto_approve_reviews(self, request, queryset):
        queryset.update(status='approve')
    def auto_disapprove_reviews(self, request, queryset):
        queryset.update(status='disapprove')

    auto_approve_reviews.short_description = "Auto-Approve all Reviews"
    auto_disapprove_reviews.short_description = "Auto-Disapprove Reviews"


    # change_list_template = "button_form.html"

admin.site.site_title = 'AI REVIEW SuperAdmin Portal'
admin.site.register(ProductReviews, ProductReviewsListAdmin)




@admin.register(ReviewFormDesign)
class ReviewFormDesignAdmin(admin.ModelAdmin):
    list_display = ('domain', 'button_color', 'button_text_color', 'label_text_color', 'background_color', 'updated_at')
    search_fields = ('domain',)
    list_filter = ('updated_at',)

@admin.register(ReviewListDesign)
class ReviewListDesignAdmin(admin.ModelAdmin):
    list_display = ('domain', 'content_text_color', 'star_rating_color', 'reviewer_name_color', 'updated_at')
    search_fields = ('domain',)
    list_filter = ('updated_at',)
