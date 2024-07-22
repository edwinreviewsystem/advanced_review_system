from django.contrib import admin
from .models import *
from django.utils.html import format_html
from django.conf import settings


class ProductReviewsListAdmin(admin.ModelAdmin):
    list_display = ('id', 'review_one_line', 'star_rating', 'email', 'domain', 'display_image', 'status', 'created_at')
    list_display_links = ('id', 'domain', 'status')
    search_fields = ('email', 'domain', 'status')
    list_filter = ('created_at','domain','status')
    list_per_page = 20
    actions = ['auto_approve_reviews', 'auto_pending_reviews']
    

    def display_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="70px" height="60px" />'.format(obj.image.url)
            )
        
        return "-"
    display_image.short_description = "Uploaded Image"

    def review_one_line(self, obj):
        return obj.review[:22] + '..' if len(obj.review) > 22 else obj.review
    review_one_line.short_description = 'Generated Review'

    def auto_approve_reviews(self, queryset):
        queryset.update(status='approve')
    def auto_pending_reviews(self, queryset):
        queryset.update(status='pending')

    auto_approve_reviews.short_description = "Approve all Reviews"
    auto_pending_reviews.short_description = "Make status- Pending"


admin.site.register(ProductReviews, ProductReviewsListAdmin)

@admin.register(ReviewSettings)
class ReviewSettingsAdmin(admin.ModelAdmin):
    list_display = ('auto_approve', 'id')
    list_filter = ('auto_approve',)
    list_display_links = ('id', 'auto_approve')


@admin.register(ReviewFormDesign)
class ReviewFormDesignAdmin(admin.ModelAdmin):
    list_display = ('domain', 'generate_button_color', 'generate_button_text_color', 'button_color', 'button_text_color', 'label_text_color', 'background_color', 'updated_at')
    search_fields = ('domain',)
    list_filter = ('updated_at',)

@admin.register(ReviewListDesign)
class ReviewListDesignAdmin(admin.ModelAdmin):
    list_display = ('domain', 'content_text_color', 'star_rating_color', 'reviewer_name_color', 'updated_at')
    search_fields = ('domain',)
    list_filter = ('updated_at',)
