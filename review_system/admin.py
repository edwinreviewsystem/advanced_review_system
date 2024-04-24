from django.contrib import admin
from .models import ProductReviews, ReviewFormDesign, ReviewListDesign
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

class ReviewFormDesignAdmin(admin.ModelAdmin):
    list_display = ('id', 'field_name', 'color_value')
admin.site.register(ReviewFormDesign, ReviewFormDesignAdmin)

class ReviewListDesignAdmin(admin.ModelAdmin):
    list_display = ('id', 'element_name', 'color_value')
admin.site.register(ReviewListDesign, ReviewListDesignAdmin)
