from django.contrib import admin
from .models import *
from django.utils.html import format_html
from django import forms
from django.urls import reverse
from urllib.parse import urlencode
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

class ReviewFormDesignForm(forms.ModelForm):
    class Meta:
        model = ReviewFormDesign
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'site' in self.fields:
            self.fields['site'].widget.can_add_related = False
            self.fields['site'].widget.can_change_related = False
            self.fields['site'].widget.can_view_related = False

@admin.register(ReviewFormDesign)
class ReviewFormDesignAdmin(admin.ModelAdmin):
    form = ReviewFormDesignForm
    list_display = (
        'get_domain',
        'generate_button',
        'generate_button_text',
        'button_color',
        'button_text_color',
        'label_text_color',
        'background_color',
        'updated_at'
    )
    fields = (
        'generate_button',
        'generate_button_text',
        'button_color',
        'button_text_color',
        'label_text_color',
        'background_color',
    )
    search_fields = ('site__domain',)
    list_filter = ('updated_at',)

    def get_domain(self, obj):
        return obj.site.domain if obj.site and obj.site.domain else "-"
    get_domain.short_description = "Domain"

class ReviewListDesignForm(forms.ModelForm):
    class Meta:
        model = ReviewListDesign
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'site' in self.fields:
            self.fields['site'].widget.can_add_related = False
            self.fields['site'].widget.can_change_related = False
            self.fields['site'].widget.can_view_related = False

@admin.register(ReviewListDesign)
class ReviewListDesignAdmin(admin.ModelAdmin):
    form = ReviewListDesignForm
    list_display = (
        'get_domain',
        'primary_btn_color',
        'btn_border_radius',
        'primary_button_position',
        'updated_at'
    )
    fields = (
        "primary_btn_color",
        "btn_border_radius",
        "primary_button_position",
        "content_text_color",
        "star_rating_color",
        "reviewer_name_color",
        "review_color",
    )
    search_fields = ('site__domain',)
    list_filter = ('updated_at',)

    def get_domain(self, obj):
        return obj.site.domain if obj.site and obj.site.domain else "-"
    get_domain.short_description = "Domain"


class CustomDateInput(forms.DateInput):
    input_type = 'date'
    format = '%Y-%m-%d'

    def __init__(self, *args, **kwargs):
        kwargs['format'] = self.format
        super().__init__(*args, **kwargs)


class CustomerAdminForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CustomerAdminForm, self).__init__(*args, **kwargs)
        optional_fields = ['last_name', 'profile_img', 'password']
        for field in optional_fields:
            self.fields[field].required = False

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password and not password.startswith('$2y$'):
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed_password.decode('utf-8')
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
        'password',
        'platform',
        'activated',
        'profile_img',
    )
    list_filter = ('email',)
    search_fields = ('email',)

    def manage_sites(self, obj):
        """
        Link to the Sites changelist filtered by:
            • the chosen customer (via reverse FK path)
            • only *active* SiteUser links
        """
        if not SiteUser.objects.filter(customer=obj).exists():
            return "-"

        params = urlencode({
            'siteuser__customer__id__exact': obj.pk,   # filter by this customer
            'siteuser__status__exact':     'active',   # and only active links
        })
        url = f"{reverse('admin:review_system_sites_changelist')}?{params}"
        return format_html(
            '<a href="{}" style="color:#007bff;font-weight:500;'
            'text-decoration:underline;">Manage&nbsp;Sites</a>', url
        )
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
    FILTER_PARAM = "siteuser__customer__id__exact"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        cust_id = request.GET.get('siteuser__customer__id__exact')
        if cust_id:
            from review_system.models import Customer
            c = Customer.objects.filter(pk=cust_id).first()
            if c:
                name = " ".join(filter(None, [c.first_name, c.last_name])) or c.email
                extra_context['title'] = f"Manage Sites for {name}"
        else:
            extra_context['title'] = "Manage Sites"

        extra_context['has_add_permission'] = False
        return super().changelist_view(request, extra_context=extra_context)

    SAFE_LOOKUPS = {
        'siteuser__customer__id__exact',
        'siteuser__status__exact',
    }

    def lookup_allowed(self, lookup, value):
        """
        Let Django admin know these look‑ups are intentional and safe.
        """
        if lookup in self.SAFE_LOOKUPS:
            return True
        return super().lookup_allowed(lookup, value)

    def get_queryset(self, request):
        qs = (super()
              .get_queryset(request)
              .prefetch_related("plansubscription_set")
              .distinct())

        # remember whose sites we’re showing – available to every other method
        self._cust_id = request.GET.get(self.FILTER_PARAM)
        return qs

    # --- Custom Display Columns for List View ---
    def site_display(self, obj):
        return obj.domain
    site_display.short_description = "Site"

    def _sub_for_customer_1(self, obj):
        qs = PlanSubscription.objects.filter(site=obj)
        if getattr(self, "_cust_id", None):
            qs = qs.filter(user_id=self._cust_id)
        return qs.select_related("plan", "user").order_by("-created_at").first()


    # 2⃣  Status column – now from PlanSubscription, not SiteUser
    def get_status(self, obj):
        sub = self._sub_for_customer_1(obj)
        return sub.status.title() if sub and sub.status else "-"
    get_status.short_description = "Status"


    # 3⃣  Plan column – reuse the same helper
    def get_plan(self, obj):
        sub = self._sub_for_customer_1(obj)
        return f"{sub.plan.name} ({sub.plan.duration})" if sub and sub.plan else "-"
    get_plan.short_description = "Plan"

    def view_action(self, obj):
        """
        Build “…/sites/<pk>/change/?siteuser__customer__id__exact=<cust>”.
        That query‑string survives every admin link without being mangled.
        """
        base = reverse("admin:review_system_sites_change", args=[obj.pk])
        extra = (
            f"?{urlencode({self.FILTER_PARAM: self._cust_id})}"
            if getattr(self, "_cust_id", None) else ""
        )
        return format_html(
            '<a href="{}" style="color:#007bff;font-weight:500;'
            'text-decoration:underline;">View</a>', base + extra
        )
    view_action.short_description = "Actions"

    def _sub_for_customer(self, obj):
        if getattr(self, "_cust_id", None):
            return (
                PlanSubscription.objects
                .filter(site=obj, user_id=self._cust_id)
                .select_related("plan", "user")
                .order_by("-created_at")            # newest if multiple
                .first()
            )
        # fallback – should never run when coming from “Manage Sites”
        return (
            PlanSubscription.objects
            .filter(site=obj)
            .select_related("plan", "user")
            .first()
        )

    # --- Read‑only fields ---
    def readonly_customer_email(self, obj):
        sub = self._sub_for_customer(obj)
        return sub.user.email if sub and sub.user else "-"
    readonly_customer_email.short_description = "Customer Email"

    def readonly_domain(self, obj):
        sub = self._sub_for_customer(obj)
        return sub.site.domain if sub and sub.site else "-"
    readonly_domain.short_description = "Domain"

    def readonly_plan_name(self, obj):
        sub = self._sub_for_customer(obj)
        return f"{sub.plan.name} ({sub.plan.duration})" if sub and sub.plan else "-"
    readonly_plan_name.short_description = "Plan Name"

    def readonly_start_date(self, obj):
        sub = self._sub_for_customer(obj)
        return sub.start_date if sub else "-"
    readonly_start_date.short_description = "Start Date"

    def readonly_end_date(self, obj):
        sub = self._sub_for_customer(obj)
        return sub.end_date if sub else "-"
    readonly_end_date.short_description = "End Date"

    def readonly_is_trial(self, obj):
        sub = self._sub_for_customer(obj)
        return sub.is_trial if sub else "-"
    readonly_is_trial.short_description = "Is Trial"

    # Make all fields read-only and hide save buttons
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    

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