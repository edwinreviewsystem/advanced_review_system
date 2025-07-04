from django.contrib import admin
from .models import *
from django.utils.html import format_html
from django import forms
from django.urls import reverse
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
    list_display = ('domain', 'primary_btn_color', 'btn_border_radius', 'primary_button_position', 'updated_at')
    fields = (
        "domain",
        "primary_btn_color",
        "btn_border_radius",
        "primary_button_position",
        "content_text_color",
        "star_rating_color",
        "reviewer_name_color",
        "review_color",
    )
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

    def __init__(self, *args, **kwargs):
        super(CustomerAdminForm, self).__init__(*args, **kwargs)
        optional_fields = ['last_name', 'date_start', 'date_end', 'plan_price', 'profile_img', 'password']
        for field in optional_fields:
            self.fields[field].required = False

        self.fields['plan'].widget.can_add_related = False
        self.fields['plan'].widget.can_change_related = False
        self.fields['plan'].widget.can_delete_related = False
        self.fields['plan'].widget.can_view_related = False

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password and not password.startswith('$2y$'):
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed_password.decode('utf-8')  # Store it as a string
        return password

@admin.register(Plans)
class PlansAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "features", "duration", "price", "created_at", "updated_at")
    list_filter = ("name", "duration")


class CustomerAdmin(admin.ModelAdmin):
    form = CustomerAdminForm
    list_display = ('id', 'plan', 'email', 'domain_name', 'first_name', 'last_name', 'platform', 'activated', 'created_at')
    fields = (
        'domain_name',
        'email',
        'first_name',
        'last_name',
        'date_start',
        'date_end',
        'password',
        'plan_price',
        'plan',
        'platform',
        'activated',
        'profile_img',
    )
    list_filter = ('email',)
    search_fields = ('email',)

    # def manage_sites(self, obj):
    #     sites = obj.sites_set.all()
    #     if not sites:
    #         return "No Sites"
        
    #     links = []
    #     for site in sites:
    #         url = reverse('admin:review_system_sites_change', args=[site.pk])  # Use your actual app name
    #         links.append(f'<a href="{url}">{site.pk}</a>')

    #     return format_html("<br>".join(links))

    # manage_sites.short_description = "Manage Sites"

    # def get_associated_plans(self, obj):
    #     plans = obj.sites_set.select_related('plan').all()
    #     display = {
    #         f"{site.plan.name} ({site.plan.duration})"
    #         for site in plans
    #         if site.plan  # skip if plan is None
    #     }
    #     return ", ".join(display) if display else "-"
    
    # get_associated_plans.short_description = "Plan Info"

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

@admin.register(Sites)
class SitesAdmin(admin.ModelAdmin):
    list_display = ('domain', 'created_at', 'updated_at')
    fields = (
        "domain",
    )
    search_fields = ('domain',)
    list_filter = ('updated_at',)

# @admin.register(CollaboratorInvitations)
# class CollaboratorInvitationsAdmin(admin.ModelAdmin):
#     list_display = ("site_id", "email", "token", "accepted")
#     fields = ("site_id", "email", "token", "accepted")
#     search_fields = ('site_id',)

# @admin.register(Collaborator)
# class CollaboratorAdmin(admin.ModelAdmin):
#     list_display = ("customer", "user_id", "created_at", "updated_at")
#     fields = ("customer", "user_id")
#     search_fields = ('customer',)
#     list_filter = ('updated_at',)