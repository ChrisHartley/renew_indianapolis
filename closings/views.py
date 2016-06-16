from django.shortcuts import render

from applications.models import Application
# Create your views here.
class ApplicationPurchaseAgreement(DetailView):
    model = Application
    context_object_name = 'application'
    template_name = 'purchase_agreement.html'
