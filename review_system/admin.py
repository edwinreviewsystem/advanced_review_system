from django.contrib import admin
from .models import *
from django.utils.html import format_html
from django import forms
from django.urls import reverse
from django.db.models import OuterRef, Subquery
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
    list_display = ('id', 'email', 'manage_sites', 'first_name', 'last_name', 'platform', 'activated', 'created_at')
    fields = (
        'email',
        'first_name',
        'last_name',
        'date_start',
        'date_end',
        'password',
        'plan_price',
        'platform',
        'activated',
        'profile_img',
    )
    list_filter = ('email',)
    search_fields = ('email',)

    def manage_sites(self, obj):
        site_ids = SiteUser.objects.filter(customer=obj, status='active').values_list("site__id", flat=True).distinct()
        
        if not site_ids:
            return ""

        query_string = "&".join([f"id__in={site_id}" for site_id in site_ids])
        url = f"{reverse('admin:review_system_sites_changelist')}?{query_string}"

        return format_html('<a href="{}" style="color: #007bff; font-weight: 500; text-decoration:underline;">Manage Sites</a>', url)
    
    manage_sites.short_description = "Sites"

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
    list_display = ('site_display', 'get_status', 'get_plan', 'view_action')
    search_fields = ('domain',)
    list_filter = ('updated_at',)
    readonly_fields = (
        'readonly_customer_email', 'readonly_domain',
        'readonly_plan_name', 'readonly_start_date', 'readonly_end_date'
    )
    fields = (
        'readonly_customer_email',
        'readonly_domain',
        'readonly_plan_name',
        'readonly_start_date',
        'readonly_end_date',
        'readonly_is_trial',
    )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        # Extract customer email from the query filter (id__in), if present
        customer_first_name = None
        customer_last_name = None
        site_ids = request.GET.getlist("id__in")

        if site_ids:
            from review_system.models import SiteUser
            site_user = (
                SiteUser.objects
                .filter(site__id__in=site_ids, status='active')
                .select_related("customer")
                .first()
            )
            if site_user and site_user.customer:
                customer_first_name = site_user.customer.first_name
                customer_last_name = site_user.customer.last_name

        if customer_first_name and customer_last_name:
            extra_context['title'] = f"Manage Sites for {customer_first_name} {customer_last_name}"
        elif customer_first_name:
            extra_context['title'] = f"Manage Sites for {customer_first_name}"
        else:
            extra_context['title'] = "Manage Sites"

        extra_context['has_add_permission'] = False  # Hides the “ADD SITE +” button

        return super().changelist_view(request, extra_context=extra_context)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('plansubscription_set')

    # --- Custom Display Columns for List View ---
    def site_display(self, obj):
        return obj.domain
    site_display.short_description = "Site"

    # With active status
    # def get_plan_subscription(self, obj):
    #     return PlanSubscription.objects.filter(site=obj, status='active').select_related('plan', 'user').first()

    # Without active status
    def get_plan_subscription(self, obj):
        return PlanSubscription.objects.filter(site=obj).select_related('plan', 'user').first()

    def get_status(self, obj):
        # Fetch the SiteUser entry for this site where status is 'active'
        site_user = SiteUser.objects.filter(site=obj, status='active').first()
        return site_user.status.title() if site_user and site_user.status else "-"
    get_status.short_description = 'Status'

    def get_plan(self, obj):
        sub = self.get_plan_subscription(obj)
        return f"{sub.plan.name} ({sub.plan.duration})" if sub and sub.plan else "-"
    get_plan.short_description = 'Plan'

    def view_action(self, obj):
        return format_html(
            '<a href="{}" style="color: #007bff; font-weight: 500; text-decoration:underline;">View</a>',
            f"/admin/review_system/sites/{obj.pk}/change/"
        )
    view_action.short_description = 'Actions'

    # --- Read-only Fields for Detail View ---
    def readonly_customer_email(self, obj):
        sub = self.get_plan_subscription(obj)
        return sub.user.email if sub and sub.user else "-"
    readonly_customer_email.short_description = "Customer Email"

    def readonly_domain(self, obj):
        return obj.domain
    readonly_domain.short_description = "Domain"

    def readonly_plan_name(self, obj):
        sub = self.get_plan_subscription(obj)
        return sub.plan if sub and sub.plan else "-"
    readonly_plan_name.short_description = "Plan Name"

    def readonly_start_date(self, obj):
        sub = self.get_plan_subscription(obj)
        return sub.start_date if sub else "-"
    readonly_start_date.short_description = "Start Date"

    def readonly_end_date(self, obj):
        sub = self.get_plan_subscription(obj)
        return sub.end_date if sub else "-"
    readonly_end_date.short_description = "End Date"

    def readonly_is_trial(self, obj):
        sub = self.get_plan_subscription(obj)
        return sub.is_trial if sub else "-"
    readonly_is_trial.short_description = "Is Trial"

    # Make all fields read-only and hide save buttons
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save'] = False
        extra_context['show_save_and_continue'] = False
        extra_context['show_save_and_add_another'] = False
        extra_context['show_delete'] = False

        # Trick to hide "Close" by setting the form to be readonly and empty
        request._dont_enforce_csrf_checks = True  # optional, to be safe with CSRF checks disabled
        self.readonly_fields = self.readonly_fields  # force all fields to readonly
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

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