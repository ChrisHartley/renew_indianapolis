from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from .models import ApplicantProfile, Organization
from applications.models import Application

class ApplicantProfileInline(admin.StackedInline):
    model = ApplicantProfile
    can_delete = False
    verbose_name_plural = 'profile'

# class ApplicantProfileAdmin(admin.ModelAdmin):
    #search_fields = ('organization', 'phone_number','mailing_address_line1','mailing_address_line2','mailing_address_line3')

class OrganizationInline(admin.TabularInline):
    model = Organization
    extra = 0

class SimpleUserInline(admin.TabularInline):
    model = User
    extra = 0
    inlines = [OrganizationInline]

class ApplicantProfileAdmin(admin.ModelAdmin):
    model = ApplicantProfile
    readonly_fields = ('user_email', 'user_first_name', 'user_last_name', 'count_applications', 'external_system_id')
    list_display = ('user_email', 'user_first_name', 'user_last_name', 'phone_number', 'mailing_address_line1', 'mailing_address_line2', 'mailing_address_line3', 'mailing_address_city', 'mailing_address_state', 'mailing_address_zip', 'count_applications')
    fields = ('user_email', 'user_first_name', 'user_last_name', 'phone_number', 'mailing_address_line1', 'mailing_address_line2', 'mailing_address_line3', 'mailing_address_city', 'mailing_address_state', 'mailing_address_zip', 'count_applications', 'external_system_id')
    search_fields = ('user__email', 'phone_number', 'user__first_name', 'user__last_name')

    #inlines = [OrganizationInline]

    def user_first_name(self, obj):
        return obj.user.first_name

    def user_last_name(self, obj):
        return obj.user.last_name

    def user_email(self, obj):
        return obj.user.email

    def count_applications(self, obj):
        count = Application.objects.filter(user__exact=obj.user).exclude(status__exact=Application.INITIAL_STATUS).count()
        summary_link = '<a href="{}">{}</a>'.format(
            reverse("admin:app_list", args=('applications',))+'application/?q={}'.format(obj.user.email,), count)
        return mark_safe(summary_link)
    count_applications.short_description = 'Application count'

class OrganiationAdmin(admin.ModelAdmin):
    model = Organization
    readonly_fields = ('external_system_id',)

class UserAdmin(UserAdmin):
    inlines = (ApplicantProfileInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Organization, OrganiationAdmin)
admin.site.register(ApplicantProfile, ApplicantProfileAdmin)
#admin.site.register(ApplicantProfile, ApplicantProfileAdmin)
