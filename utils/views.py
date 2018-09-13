# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic.base import TemplateView
from django.conf import settings

class DonateView(TemplateView):
    template_name = 'donate.html'

    def get_context_data(self, **kwargs):
        context = super(DonateView, self).get_context_data(**kwargs)
        context['STRIPE_API_KEY'] = settings.STRIPE_PUBLIC_API_KEY
        return context
