# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic.edit import FormView, CreateView
from .forms import InspectionRequestForm
from .models import InspectionRequest
from property_inventory.models import Property
from django.urls import reverse_lazy
from django.contrib import messages

class InspectionRequestFormView(CreateView):
    model = InspectionRequest
    template_name = 'project_agreement_management/inspection_request_form.html'
    form_class = InspectionRequestForm
    success_url = reverse_lazy('applicants_home')

    def get_initial(self):
        initial = super(InspectionRequestFormView, self).get_initial()
        if self.kwargs.get('parcel') is not None:
            initial['Property'] = Property.objects.filter(parcel__contains=self.kwargs['parcel']).first()
        return initial

    def form_valid(self, form):
        messages.add_message(self.request, messages.INFO, "Inspection request submitted!")

        return super(InspectionRequestFormView, self).form_valid(form)
