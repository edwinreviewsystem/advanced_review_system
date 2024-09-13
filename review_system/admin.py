from django.contrib import admin
from .models import *
from django.utils.html import format_html
from django import forms
import bcrypt


class ProductReviewsListAdmin(admin.ModelAdmin):
    list_display = ('id', 'review_one_line', 'star_rating', 'email', 'domain', 'display_image', 'status', 'source', 'created_at')
    list_display_links = ('id', 'domain', 'status')
    search_fields = ('email', 'domain', 'status')
    list_filter = ('created_at', 'domain', 'status')
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
    list_display = ('auto_approve', 'id', 'domain')
    list_filter = ('auto_approve',)
    list_display_links = ('id', 'auto_approve')


@admin.register(ReviewFormDesign)
class ReviewFormDesignAdmin(admin.ModelAdmin):
    list_display = ('domain', 'generate_button', 'generate_button_text', 'button_color', 'button_text_color', 'label_text_color', 'background_color', 'updated_at')
    search_fields = ('domain',)
    list_filter = ('updated_at',)


@admin.register(ReviewListDesign)
class ReviewListDesignAdmin(admin.ModelAdmin):
    list_display = ('domain', 'content_text_color', 'star_rating_color', 'reviewer_name_color', 'updated_at')
    search_fields = ('domain',)
    list_filter = ('updated_at',)


class CustomDateInput(forms.DateInput):
    input_type = 'date'
    format = '%Y-%m-%d'

    def __init__(self, *args, **kwargs):
        kwargs['format'] = self.format
        super().__init__(*args, **kwargs)


class CustomerAdminForm(forms.ModelForm):
    date_start = forms.DateField(widget=CustomDateInput(format='%d-%m-%Y'))
    date_end = forms.DateField(widget=CustomDateInput(format='%d-%m-%Y'))

    class Meta:
        model = Customer
        fields = '__all__'

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password and not password.startswith('$2y$'):
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed_password.decode('utf-8')  # Store it as a string
        return password


class CustomerAdmin(admin.ModelAdmin):
    form = CustomerAdminForm
    list_display = ('id', 'email', 'domain_name', 'first_name', 'last_name', 'display_profile_image', 'activated', 'created_at')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['password'].widget = forms.PasswordInput(render_value=True)
        return form

    def save_model(self, request, obj, form, change):
        password = form.cleaned_data.get('password')
        if password and not password.startswith('$2y$'):  
            salt = bcrypt.gensalt()
            obj.password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        super().save_model(request, obj, form, change)

    def display_profile_image(self, obj):
        if obj.profile_img:
            return format_html(
                '<img src="{}" width="70px" height="60px" />'.format(obj.profile_img.url)
            )
        return "-"
    display_profile_image.short_description = "Profile Image"


admin.site.register(Customer, CustomerAdmin)
