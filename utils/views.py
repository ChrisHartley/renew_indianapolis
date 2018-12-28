# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic.base import TemplateView
from django.conf import settings
import stripe
from django.contrib import messages
from django.http import JsonResponse


class DonateView(TemplateView):
    template_name = 'donate.html'
#    http_method_names = ['post','get']

    def get_context_data(self, **kwargs):
        context = super(DonateView, self).get_context_data(**kwargs)
        context['STRIPE_API_KEY'] = settings.STRIPE_PUBLIC_API_KEY
        return context

    def post(self, request, *args, **kwargs):
        token = request.POST.get('token')
        amount = request.POST.get('amount')
        stripe.api_key = settings.STRIPE_SECRET_API_KEY

        print("Amount: {}".format(amount,))
        try:
        # Use Stripe's library to make requests...
            charge = stripe.Charge.create(
                amount=int(amount),
                currency="usd",
                description="Donation - Renew Indianapolis",
                source=token,
                #receipt_email="{0}".format(obj.closing.application.user.email,),
                #metadata={"donation": obj.slug},
            )
        except stripe.error.CardError as e:
        # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err  = body['error']

            messages.add_message(request, messages.ERROR, 'Our credit card processor reported a problem with your card.')

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.add_message(request, messages.ERROR, 'Temporary error, your card has not been charged. Please try again in a few moments.')

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.add_message(request, messages.ERROR, '#1 There was a problem with our system, your card has not been charged.')

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            messages.add_message(request, messages.ERROR, '#2 There was a problem with our system, your card has not been charged.')
            print(e)
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.add_message(request, messages.ERROR, '#3 There was a problem with our system, your card has not been charged.')

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email

            messages.add_message(request, messages.ERROR, '#4 There was a problem with our system, your card has not been charged.')

        except Exception as e:
            # Something else happened, completely unrelated to Stripe

            messages.add_message(request, messages.ERROR, '#5 There was a problem with our system, your card has not been charged.')

        else:
            messages.add_message(request, messages.SUCCESS, 'Your card has been charged, thank you for your donation.')

        django_messages = []

        for message in messages.get_messages(request):
            django_messages.append({
                "level": message.level,
                "message": message.message,
                "extra_tags": message.tags,
            })
        return JsonResponse(django_messages, safe=False)
