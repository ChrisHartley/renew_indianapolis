from django.shortcuts import render
from django.core.urlresolvers  import reverse_lazy
# Create your views here.
from .forms import DumpPhotosForm
from django.views.generic.edit import FormView
from django.contrib.messages.views import SuccessMessageMixin

class DumpPhotosView(SuccessMessageMixin, FormView):
    template_name = 'photos.html'
    form_class = DumpPhotosForm
    success_url = reverse_lazy('admin_add_photos')
    success_message = "%(prop)s images saved."

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.save_photos()
        return super(DumpPhotosView, self).form_valid(form)
