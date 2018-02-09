from django.shortcuts import get_object_or_404, render_to_response
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.views.generic import DetailView, View
import stripe
from decimal import *
from datetime import date
from applications.models import Application
from .models import processing_fee, title_company, closing
from .forms import TitleCompanyChooser
from django.contrib import messages
from django.utils.text import slugify
from wsgiref.util import FileWrapper
from django.contrib.admin.views.decorators import staff_member_required

class ClosingDepositSlipDetailView(DetailView):
    model = closing
    context_object_name = 'closing'
    template_name = 'closing_deposit_slip.html'

class ApplicationPurchaseAgreement(DetailView):
    model = Application
    context_object_name = 'application'
    template_name = 'purchase_agreement.html'
    def get_context_data(self, **kwargs):
        #print "hello", self
        context = super(ApplicationPurchaseAgreement, self).get_context_data(**kwargs)
        #print "hello", self
        #self.object.meeting_set
        context['approval_date'] = self.object.meeting
        return context

class ProcessingFeePaymentPage(DetailView):
    context_object_name = 'processing_fee'
    template_name = 'processing_fee_payment.html'
    def get_context_data(self, **kwargs):
        context = super(ProcessingFeePaymentPage, self).get_context_data(**kwargs)
        context['form'] = TitleCompanyChooser

        #context['creditCardFees'] = (int(self.object.amount_due)*settings.COMPANY_SETTINGS['CREDIT_CARD_PERCENTAGE_FEE'])+settings.COMPANY_SETTINGS['CREDIT_CARD_FLAT_FEE']*100
        #context['creditCardFees'] = settings.STRIPE_FEES[self.object.amount_due]

        #print context['creditCardFees'], context['amountForStripe']
        #context['amountForStripe']
        if self.object.amount_due == settings.COMPANY_SETTINGS['SIDELOT_PROCESSING_FEE']:
            context['creditCardFees'] = settings.COMPANY_SETTINGS['SIDELOT_PROCESSING_STRIPE_FEE']
        elif self.object.amount_due == settings.COMPANY_SETTINGS['STANDARD_PROCESSING_FEE']:
            context['creditCardFees'] = settings.COMPANY_SETTINGS['STANDARD_PROCESSING_STRIPE_FEE']
        context['amountForStripe'] = int(int(self.object.amount_due*100)+context['creditCardFees']) # $100 costs $3.30, $200 costs 6.28
        context['display_credit_card_fee'] = '{:20,.2f}'.format(context['creditCardFees']/100.0)
        context['STRIPE_API_KEY'] = settings.STRIPE_PUBLIC_API_KEY
        context['COMPANY_SETTINGS'] = settings.COMPANY_SETTINGS
        return context
    def get_object(self):
        if self.request.user.is_staff == True:
            return get_object_or_404(processing_fee, id=self.kwargs['id'])
        else:
            return get_object_or_404(processing_fee, id=self.kwargs['id'], closing__application__user__exact=self.request.user)

class ProcessingFeePaidPage(View):

    http_method_names = ['post','get']

    def post(self, request, *args, **kwargs):
        obj = get_object_or_404(processing_fee, pk=kwargs['id'])
        token = request.POST.get('stripeToken')
        amount = obj.amount_due
        stripe.api_key = settings.STRIPE_SECRET_API_KEY
        if obj.amount_due == settings.COMPANY_SETTINGS['SIDELOT_PROCESSING_FEE']:
            credit_card_fee = settings.COMPANY_SETTINGS['SIDELOT_PROCESSING_STRIPE_FEE']
        elif obj.amount_due == settings.COMPANY_SETTINGS['STANDARD_PROCESSING_FEE']:
            credit_card_fee = settings.COMPANY_SETTINGS['STANDARD_PROCESSING_STRIPE_FEE']
        try:
        # Use Stripe's library to make requests...
            charge = stripe.Charge.create(
                amount=int(int(obj.amount_due*100)+credit_card_fee), # $100 costs $3.30, $200 costs 6.28
                currency="usd",
                description="Processing fee - {0}".format(obj.closing.application.Property),
                source=token,
                metadata={"property_slug": obj.slug},
            )
        except stripe.error.CardError as e:
        # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err  = body['error']

            #print "Status is: %s" % e.http_status
            #print "Type is: %s" % err['type']
            #print "Code is: %s" % err['code']
            # param is '' in this case
            #print "Param is: %s" % err['param']
            #print "Message is: %s" % err['message']
            messages.add_message(request, messages.ERROR, 'Our credit card processor reported a problem with your card.')
            return HttpResponse("Card error: {0}".format(err))
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            #print e
            messages.add_message(request, messages.ERROR, 'Temporary error, your card has not been charged. Please try again in a few moments.')
            return HttpResponse("Rate Limit Error: {0}".format(e))
        except stripe.error.InvalidRequestError as e:
            #print e
            messages.add_message(request, messages.ERROR, 'There was a problem with our system, your card has not been charged.')
            return HttpResponse("Invalid Stripe API request: {0}".format(e))
            # Invalid parameters were supplied to Stripe's API
        except stripe.error.AuthenticationError as e:
            #print e
            messages.add_message(request, messages.ERROR, 'There was a problem with our system, your card has not been charged.')
            return HttpResponse("Invalid AuthenticationError request: {0}".format(e))
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
        except stripe.error.APIConnectionError as e:
            #print e
            messages.add_message(request, messages.ERROR, 'There was a problem with our system, your card has not been charged.')
            return HttpResponse("Stripe connection error request: {0}".format(e))
            # Network communication with Stripe failed
        except stripe.error.StripeError as e:
            #print e
            messages.add_message(request, messages.ERROR, 'There was a problem with our system, your card has not been charged.')
            return HttpResponse("Stripe error: {0}".format(e))
            # Display a very generic error to the user, and maybe send
            # yourself an email
        except Exception as e:
            #print e
            messages.add_message(request, messages.ERROR, 'There was a problem with our system, your card has not been charged.')
            return HttpResponse("Edge case error: {0}".format(e))
            # Something else happened, completely unrelated to Stripe

        obj.amount_received = int(request.POST.get('amountForStripe')) / 100
        if obj.amount_received < obj.amount_due:
            messages.add_message(request, messages.ERROR, 'There was a problem with our system, please contact support.')
            return HttpResponse("Partial payments are not permitted")
        obj.stripeTokenType = request.POST.get('stripeTokenType')
        obj.stripeEmail = request.POST.get('stripeEmail')
        obj.date_paid = date.today()
        obj.paid = True
        obj.user = request.user
        closing = obj.closing
        if request.POST.get('manual_title_company_choice') != '':
            closing.title_company_freeform = request.POST.get('manual_title_company_choice')
        else:
            if request.POST.get('title_company') != '':
                try:
                    closing.title_company = title_company.objects.get(pk=request.POST.get('title_company'))
                except title_company.DoesNotExist as e:
                    messages.add_message(request, messages.ERROR, 'There was an error with your title company selection, a staff member will contact you.')
                    closing.title_company_freeform = "There was a problem with the applicant's title company selection."
            else:
                messages.add_message(request, messages.ERROR, 'You did not select a title company, a staff member will contact you.')
                closing.title_company_freeform = 'Applicant did not make a title company selection.'
        try:
            obj.save()
            closing.save()
        except Exception as e:
            print "terrible error!!!"
            messages.add_message(request, messages.ERROR, 'There was a problem with our system, please contact support.')
            return HttpResponse("Error saving payment object: {0}".format(e))
        messages.add_message(request, messages.SUCCESS, 'Your card has been charged and our staff have been notified to proceed with your closing.')
#        pf = processing_fee.objects.get(id=kwargs['id'])
#        closing = pf.closing
        prop = closing.application.Property
        slug = slugify(prop)
        return HttpResponseRedirect(reverse('application_pay_processing_fee', kwargs={'id': kwargs['id'], 'slug': slug}))
        #return HttpResponse("Everything worked for {0}".format(obj.closing.application.Property))

#
# @staff_member_required
# def send_file(request, category, filename):
#     """
#     https://www.djangosnippets.org/snippets/365/
#     Send a file through Django without loading the whole file into
#     memory at once. The FileWrapper will turn the file object into an
#     iterator for chunks of 8KB.
#     """
#     #possible_closings = closing.objects.filter(application__Property=property)
#     #requested_file = get_object_or_404(UploadedFile, id=id)
#     #filename = str(requested_file.supporting_document.name)
#     if category in('closings'):
#         filename = settings.MEDIA_ROOT+category+'/'+filename
#         with open(filename, 'rb') as f:
#             wrapper = FileWrapper(f)
#             content_type = mimetypes.MimeTypes().guess_type(filename)[0]
#             response = HttpResponse(wrapper, content_type=content_type)
#             response['Content-Length'] = os.path.getsize(filename)
#             response['Content-Disposition'] = 'attachment; filename="{}"'.format(os.path.basename(filename))
#             return response
#     raise Http404
