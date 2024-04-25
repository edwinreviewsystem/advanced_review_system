from django.contrib import admin
from .models import *
from django.utils.html import format_html

class ProductReviewsAdmin(admin.ModelAdmin):
    list_display = ('id','user','email', 'star_rating', 'review', 'product_name', 'domain', 'display_image','created_at')

    def display_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50px" height="50px" />'.format(obj.image.url)
            )
        return None
    display_image.short_description = "Uploaded Image"

    search_fields = ('domain', 'product_name')
    list_filter = ('star_rating', 'domain', 'product_name', 'created_at')

admin.site.register(ProductReviews, ProductReviewsAdmin)


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
