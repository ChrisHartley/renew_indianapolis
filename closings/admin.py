from django.contrib import admin
from .models import location, company_contact, mailing_address, title_company, closing

admin.site.register(location)
admin.site.register(company_contact)
admin.site.register(mailing_address)
admin.site.register(title_company)
admin.site.register(closing)
