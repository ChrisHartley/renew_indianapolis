from django.contrib import admin
from .models import annual_report

class AnnualReportAdmin(admin.ModelAdmin):
        list_display = ('created','Property', 'name', 'organization')
        #list_filter = ()
        search_fields = ('name', 'organization', 'email', 'Property__parcel', 'Property__streetAddress')
        readonly_fields = ('Property',)
        fieldset = (
            (None, {
                'fields': ('Property','Property__status')
            }),
        )


admin.site.register(annual_report, AnnualReportAdmin)
