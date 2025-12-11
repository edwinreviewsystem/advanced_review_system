from django.contrib import admin
from .models import *
from django.utils.html import format_html
from django import forms
from django.urls import reverse
from urllib.parse import urlencode
import bcrypt

from django.http import HttpResponseRedirect
from django.contrib import messages


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

class SiteAdminForm(forms.ModelForm):
    plan = forms.ModelChoiceField(
        queryset=Plans.objects.all(),
        required=False,
        label="Plan Name"
    )
    start_date = forms.DateField(required=False)
    end_date = forms.DateField(required=False)
    is_trial = forms.BooleanField(required=False)

    class Meta:
        model = Sites
        fields = ['domain', 'plan', 'start_date', 'end_date', 'is_trial']

@admin.register(Sites)
class SitesAdmin(admin.ModelAdmin):
    form = SiteAdminForm  # assume your SiteAdminForm defines: domain, plan, start_date, end_date, is_trial

    list_display = ('site_display', 'get_status', 'get_plan', 'view_action')
    search_fields = ('domain',)
    list_filter = ('updated_at',)
    FILTER_PARAM = "siteuser__customer__id__exact"

    SAFE_LOOKUPS = {
        'siteuser__customer__id__exact',
        'siteuser__status__exact',
    }

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        cust_id = request.GET.get(self.FILTER_PARAM)
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

    def lookup_allowed(self, lookup, value):
        if lookup in self.SAFE_LOOKUPS:
            return True
        return super().lookup_allowed(lookup, value)

    def get_queryset(self, request):
        qs = (super()
              .get_queryset(request)
              .prefetch_related("plansubscription_set")
              .distinct())
        # remember whose sites we’re showing
        self._cust_id = request.GET.get(self.FILTER_PARAM)
        return qs

    # -------------------------
    # Show fields on change form.
    # - When opened for a customer (via FILTER_PARAM) we show the editable fields
    #   plus the read-only "Customer Email".
    # - Otherwise fall back to default admin fields (read-only behaviour).
    # -------------------------
    def get_fields(self, request, obj=None):
        cust_id = request.GET.get(self.FILTER_PARAM)

        # 1️⃣ ADD PAGE
        if obj is None:
            # Show only fields for creating a new Site
            return ['domain', 'name']

        # 2️⃣ EDIT WITH CUSTOMER FILTER (Manage Sites → View)
        if cust_id:
            return [
                'readonly_customer_email',
                'domain', 'plan', 'start_date', 'end_date', 'is_trial'
            ]

        # 3️⃣ EDIT DIRECT FROM SITES (no customer filter)
        return [
            'readonly_customer_email',
            'domain', 'plan', 'start_date', 'end_date', 'is_trial'
        ]
        # no special customer filter -> keep previous behaviour (read-only changelist/detail)
        # return super().get_fields(request, obj)

    def get_readonly_fields(self, request, obj=None):
        # ADD page → no read-only fields
        if obj is None:
            return []

        # EDIT pages → Customer Email always read-only
        return ['readonly_customer_email']

    # -------------------------
    # Only allow changing (show save buttons) if FILTER_PARAM present.
    # Otherwise keep read-only (no save).
    # -------------------------
    def has_change_permission(self, request, obj=None):
        """
        Let Django's normal permission system handle this.
        This means:
        - If the user has change permission on Sites, they can edit from both:
            - Customer → Manage Sites
            - Direct Sites list
        - Your existing FILTER_PARAM-based logic is still used for scoping
        which PlanSubscription we touch in save_model().
        """
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False

    # -------------------------
    # Prefill the form: return a dynamic form class that sets initial for plan/start/end/is_trial
    # using the latest PlanSubscription for (site, customer).
    # -------------------------
    def get_form(self, request, obj=None, **kwargs):
        """
        Build a subclass of the configured form that sets initial values for subscription fields
        when we have an obj, using either:
        - customer-specific subscription (when FILTER_PARAM present), or
        - latest subscription for that site (when opened directly from Sites).
        """
        cust_id = request.GET.get(self.FILTER_PARAM)
        BaseForm = super().get_form(request, obj, **kwargs)  # SiteAdminForm

        class _PrefilledForm(BaseForm):
            def __init__(self, *a, **kw):
                super().__init__(*a, **kw)

                # Domain is already prefilled by the ModelForm.
                if not obj:
                    return

                try:
                    # 1) If we have customer context → filter by that user
                    if cust_id:
                        qs = (
                            PlanSubscription.objects
                            .filter(site=obj, user_id=cust_id)
                            .select_related('plan')
                        )
                    else:
                        # 2) No customer context (direct Sites) → use latest sub for this site
                        qs = (
                            PlanSubscription.objects
                            .filter(site=obj)
                            .select_related('plan')
                        )

                    sub = qs.order_by('-created_at').first()

                    if sub:
                        if 'plan' in self.fields:
                            self.fields['plan'].initial = sub.plan_id
                        if 'start_date' in self.fields:
                            self.fields['start_date'].initial = sub.start_date
                        if 'end_date' in self.fields:
                            self.fields['end_date'].initial = sub.end_date
                        if 'is_trial' in self.fields:
                            self.fields['is_trial'].initial = bool(sub.is_trial)

                except Exception:
                    # be tolerant — don't break admin for unexpected DB states
                    pass

        return _PrefilledForm

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

    def render_change_form(self, request, context, *args, **kwargs):
        # Hide unwanted buttons
        context['show_save_and_add_another'] = False
        context['show_save_and_continue'] = False
        context['show_save'] = True  # keep Save button

        return super().render_change_form(request, context, *args, **kwargs)

    def save_model(self, request, obj, form, change):
        # Save Sites.domain, name, etc. first
        super().save_model(request, obj, form, change)

        cust_id = request.GET.get(self.FILTER_PARAM)

        # 🧩 1) For ADD page without customer context, keep the old behaviour:
        # don't auto-create a subscription if we don't know the customer.
        if not change and not cust_id:
            return

        # 🧩 2) For EDIT page without FILTER_PARAM (opened directly from Sites),
        # infer the customer from the latest PlanSubscription for this site.
        if not cust_id and change:
            latest_sub = (
                PlanSubscription.objects
                .filter(site=obj)
                .order_by('-created_at')
                .first()
            )
            if not latest_sub:
                # No existing subscription to update, and no customer context
                # → nothing to do (same spirit as your previous code)
                return
            cust_id = latest_sub.user_id

        # If we still don't have a cust_id for some reason, bail out.
        if not cust_id:
            return

        # 🧩 3) Now we have a customer ID (either from FILTER_PARAM or inferred).
        sub = (
            PlanSubscription.objects
            .filter(site=obj, user_id=cust_id)
            .order_by('-created_at')
            .first()
        )

        if sub:
            # update existing subscription
            sub.plan = form.cleaned_data.get('plan') or sub.plan
            sub.start_date = form.cleaned_data.get('start_date')
            sub.end_date = form.cleaned_data.get('end_date')
            sub.is_trial = bool(form.cleaned_data.get('is_trial'))
            # Keep existing status/platform unless you want to change them explicitly
            sub.save()
        else:
            # no existing sub -> create one (same as your previous behaviour)
            PlanSubscription.objects.create(
                user_id=cust_id,
                site=obj,
                plan=form.cleaned_data.get('plan'),
                start_date=form.cleaned_data.get('start_date'),
                end_date=form.cleaned_data.get('end_date'),
                is_trial=bool(form.cleaned_data.get('is_trial')),
                status='active'
            )

    def response_change(self, request, obj):
        """
        After the user clicks Save, stay on the same page
        and show a success message.
        """
        messages.success(request, "The information has been updated.")

        # Stay on the same edit page:
        return HttpResponseRedirect(request.path)