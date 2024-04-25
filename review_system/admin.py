from django.contrib import admin
from .models import *
from django.utils.html import format_html

from django.db.models import F
from sorl.thumbnail import get_thumbnail

class ProductReviewsListAdmin(admin.ModelAdmin):
    list_display = ('id', 'domain', 'star_rating', 'review_one_line', 'name', 'email', 'display_image', 'created_at')
    list_display_links = ('id', 'domain')
    search_fields = ('name', 'email', 'domain')
    list_filter = ('created_at',)
    list_per_page = 50

    def display_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="70px" height="50px" />'.format(obj.image.url)
            )
        return None
    display_image.short_description = "Uploaded Image"


    # def display_image(self, obj):
    #     if obj.image:
    #             image = get_thumbnail(obj.image, "80x80" )
    #             return format_html('<img src="{}" width="80px" height="80px" />'.format(image.url))
    #     return None
    # display_image.short_description = "Uploaded Image"


    def review_one_line(self, obj):
        return obj.review[:45] + '..' if len(obj.review) > 50 else obj.review
    review_one_line.short_description = 'Review'

admin.site.register(ProductReviews, ProductReviewsListAdmin)



@admin.register(ReviewFormDesign)
class ReviewFormDesignAdmin(admin.ModelAdmin):
    list_display = ('domain_name', 'button_color', 'button_text_color', 'label_text_color', 'background_color', 'updated_at')
    search_fields = ('domain_name',)
    list_filter = ('updated_at',)

@admin.register(ReviewListDesign)
class ReviewListDesignAdmin(admin.ModelAdmin):
    list_display = ('domain_name', 'content_text_color', 'star_rating_color', 'reviewer_name_color', 'updated_at')
    search_fields = ('domain_name',)
    list_filter = ('updated_at',)
