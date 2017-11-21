from django.contrib import admin
from .models import ConditionReport, Room
class RoomInline(admin.TabularInline):
    model = Room
    #fields = ('date_purchased', 'date_expiring', 'amount_paid', )
    #readonly_fields=('closing',)
    extra = 3

class ConditionReportAdmin(admin.ModelAdmin):
    inlines = [RoomInline,]


admin.site.register(ConditionReport, ConditionReportAdmin)
# Register your models here.
