from django.shortcuts import render
from django.forms.models import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
# Create your views here.
from .forms import DumpPhotosForm
from .models import photo
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.contrib.messages.views import SuccessMessageMixin

class DumpPhotosView(SuccessMessageMixin, FormView):
    template_name = 'photos.html'
    form_class = DumpPhotosForm
    success_url = reverse_lazy('admin_add_photos')
    success_message = "%(prop)s images saved."

    def get_initial(self):
        initial_data = super(DumpPhotosView, self).get_initial()
        if self.request.GET.get('Property'):
            initial_data['prop'] = self.request.GET.get('Property')
        return initial_data

    def form_valid(self, form):
        form.save_photos()
        return super(DumpPhotosView, self).form_valid(form)



class PropertyPhotosView(TemplateView):
    template_name = "property_photo_display.html"
    def get_context_data(self, **kwargs):
            context = super(PropertyPhotosView, self).get_context_data(**kwargs)
            parcel = self.kwargs['parcel']
            num = self.request.GET.get('number')
            try:
                number = int(num)
            except:
                number = None
            if number:
                context['photos'] = photo.objects.filter(prop__parcel__exact=parcel).order_by('-main_photo')[:number]
            else:
                context['photos'] = photo.objects.filter(prop__parcel__exact=parcel).order_by('-main_photo')
            return context

    def render_to_response(self, context, **response_kwargs):
        """
        Creates a JSON response if requested, otherwise returns the default
        template response.
        """
        if 'json' in self.request.GET.get('format', ''):
            s = serializers.serialize('json', context.get('photos'))
            return HttpResponse(s, content_type="application/json")

        # Business as usual otherwise
        else:
            return super(PropertyPhotosView, self).render_to_response(context, **response_kwargs)
