# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from .models import Document, Application, Property
from .forms import CommIndApplicationForm, EntityMemberFormSet, EntityForm
#, CommIndDocumentFormset

# This function sends a Document to the user. Used instead of direct download so we can enforce
# permissions. In the future use a library such as fleep or magic to determine the actual
# file type and set content_type appropriately. That would help open PDFs in browser, etc.
def view_document(request, filename):
    f2 = 'documents/'+'/'.join(filename.split('/')[0:])
    d = get_object_or_404(Document, file__exact=f2)
    if d.publish is not True and request.user.is_staff is not True and request.user is not d.user:
        return HttpResponseForbidden("Permission denied.")
    else:
        f = open(d.file.path)
        response = HttpResponse(f, content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(d.file.name.split('/')[-1],)
        return response

from django.db import transaction
from .models import Entity, Person
class CommIndApplicationFormView(FormView):
    form_class = CommIndApplicationForm
    template_name = 'commind_application.html'
    success_url = '/commercial_industrial/success'
    def get_initial(self):
        initial = super(CommIndApplicationFormView, self).get_initial()
        if self.kwargs.get('parcel') is not None:
            initial['Properties'] = Property.objects.filter(parcel__contains=self.kwargs['parcel'])
        return initial

    # def get_context_data(self, **kwargs):
    #     data = super(CommIndApplicationFormView, self).get_context_data(**kwargs)
    #     if self.request.POST:
    #         data['entity_form'] = EntityForm(self.request.POST)
    #         data['entity_member_form'] = EntityMemberFormSet(self.request.POST)
    #     else:
    #         data['entity_form'] = EntityForm()
    #         data['entity_member_form'] = EntityMemberFormSet()
    #     return data

    def form_valid(self, form):
        #context = self.get_context_data()
        #entitymembers = context['entity_member_form']
    #
        if form.validate_for_submission():
            print "Form is valid"
            with transaction.atomic():
                entity = Entity(
                    user=self.request.user,
                    name=form.cleaned_data['entity_name'],
                    created=form.cleaned_data['entity_formed'],
                    date_of_creation=form.cleaned_data['entity_formed_date'],
                    location_of_creation=form.cleaned_data['entity_formed_location'],
                )
                entity.save()
                for cnt in [1,2,3,4]:
                    if form.cleaned_data['principal_{}_name'.format(cnt,)] != '':
                        person = Person(
                            entity = entity,
                            name = form.cleaned_data['principal_{}_name'.format(cnt,)],
                            title = form.cleaned_data['principal_{}_title'.format(cnt,)],
                            email = form.cleaned_data['principal_{}_email'.format(cnt,)],
                            phone = form.cleaned_data['principal_{}_phone'.format(cnt,)],
                            address = form.cleaned_data['principal_{}_address'.format(cnt,)],
                            nature_extent_of_interest = form.cleaned_data['principal_{}_ownership_share'.format(cnt,)],
                        )
                        person.save()
            self.object = form.save(commit=False)
            self.object.user = self.request.user
            self.object.entity = entity
            self.object.save() # to get id so ModelMultipleChoiceField can be saved
            self.object.Properties = form.cleaned_data['Properties']
            self.object.save()

            budget_and_financing_file = Document(
                user = self.request.user,
                file = form.cleaned_data['budget_and_financing_file'],
                file_purpose = 'Budget and Financing',
                content_object = self.object,
            )
            budget_and_financing_file.save()
            balance_sheet_file = Document(
                user = self.request.user,
                file = form.cleaned_data['balance_sheet_file'],
                file_purpose = 'Balance Sheet',
                content_object = self.object,
            )
            balance_sheet_file.save()
            development_plan_file = Document(
                user = self.request.user,
                file = form.cleaned_data['development_plan_file'],
                file_purpose = 'Development Plan',
                content_object = self.object,
            )
            development_plan_file.save()
        else:
            return self.form_invalid(form)
    #    return HttpResponseRedirect(self.get_success_url())
        return super(CommIndApplicationFormView, self).form_valid(form)

#class CommIndDocumentFormsetView(FormView):
#    form_class = CommIndDocumentFormset
#    template_name = 'commind_application_documents.html'


# class CommIndApplicationFormView(FormView):
#     form_class = CommIndApplicationForm
#     template_name = 'commind_application.html'
#     success_url = 'commercial_industrial/application/'
#     def get_initial(self):
#         initial = super(CommIndApplicationFormView, self).get_initial()
#         if self.kwargs.get('parcel') is not None:
#             initial['Properties'] = Property.objects.filter(parcel__contains=self.kwargs['parcel'])
#         return initial

class CommIndApplicationSuccessView(TemplateView):
     template_name = "commind_application_sucess.html"

class PropertyListView(ListView):
    model = Property
    template_name = 'commind_property_list.html'
