# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic.edit import FormView
from .forms import InspectionRequestForm
from property_inventory.models import Property


class InspectionRequestFormView(FormView):
    template_name = 'project_agreement_management/inspection_request_form.html'
    form_class = InspectionRequestForm
    success_url = ''

    def get_initial(self):
        initial = super(InspectionRequestFormView, self).get_initial()
        if self.kwargs.get('parcel') is not None:
            initial['Property'] = Property.objects.filter(parcel__contains=self.kwargs['parcel']).first()
        return initial

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.send_email()
        return super(ContactView, self).form_valid(form)
