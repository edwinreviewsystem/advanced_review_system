from django.contrib import admin
from .models import *
from django.utils.html import format_html

from django.db.models import F
from sorl.thumbnail import get_thumbnail
from django.conf import settings
from django.template.loader import render_to_string

class ProductReviewsListAdmin(admin.ModelAdmin):
    list_display = ('id', 'domain', 'star_rating', 'review_one_line', 'name', 'email', 'display_image', 'created_at')
    list_display_links = ('id', 'domain')
    search_fields = ('name', 'email', 'domain')
    list_filter = ('created_at',)
    list_per_page = 20


    def display_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="70px" height="60px" />'.format(obj.image.url)
            )
        # else:
        #     return format_html('<img src="static/No_image_found.jpg" width="50px" height="50px" />')
    display_image.short_description = "Uploaded Image"


    def review_one_line(self, obj):
        return obj.review[:22] + '..' if len(obj.review) > 22 else obj.review
    review_one_line.short_description = 'Review'


    def get_list_display(self, request):
        if request.path.endswith('/change/'):
            return ('domain', 'star_rating', 'review','email', 'name', 'display_image', 'product_name')
        # Use summary list display for list view
        return ('id', 'name', 'email', 'star_rating', 'review_one_line', 'domain', 'display_image', 'created_at')

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
