from django import forms

from .models import Application, Property, Note, Entity, Document, Person
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder, Div, Button, MultiField, Field, HTML, Div, LayoutObject, MultiField
from crispy_forms.bootstrap import FormActions, InlineRadios, PrependedAppendedText, InlineField, AppendedText, InlineCheckboxes
from django.urls import reverse
from applicants.widgets import AddAnotherWidgetWrapper
from django.forms import inlineformset_factory
from django.forms.models import formset_factory
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError

#CommIndDocumentFormset = inlineformset_factory(Application, Document)


class Formset(LayoutObject):
    """
    Renders an entire formset, as though it were a Field.
    Accepts the names (as a string) of formset and helper as they
    are defined in the context

    Examples:
        Formset('contact_formset')
        Formset('contact_formset', 'contact_formset_helper')
    """

    template = "forms/formset.html"

    def __init__(self, formset_context_name, helper_context_name=None,
                 template=None, label=None):

        self.formset_context_name = formset_context_name
        self.helper_context_name = helper_context_name

        # crispy_forms/layout.py:302 requires us to have a fields property
        self.fields = []

        # Overrides class variable with an instance level variable
        if template:
            self.template = template

    def render(self, form, form_style, context, **kwargs):
        formset = context.get(self.formset_context_name)
        helper = context.get(self.helper_context_name)
        # closes form prematurely if this isn't explicitly stated
        if helper:
            helper.form_tag = False

        context.update({'formset': formset, 'helper': helper})
        return render_to_string(self.template, context.flatten())

class EntityForm(forms.ModelForm):
    class Meta:
        model = Entity
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        super(EntityForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = 'form-horizontal'
        self.helper.field_class = 'col-lg-6'
        self.helper.label_class = 'col-lg-4'
        self.helper.render_unmentioned_fields = False
        self.helper.layout = Layout(
            Field('name'),
            Field('date_of_creation'),
            Field('location_of_creation'),
            )

class EntityMemberForm(forms.ModelForm):
    class Meta:
        model = Person
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(EntityMemberForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = 'form-horizontal'
        self.helper.field_class = 'col-lg-6'
        self.helper.label_class = 'col-lg-4'
        self.helper.render_unmentioned_fields = False
        self.helper.layout = Layout(
            Field('name'),
            Field('title'),
            Field('nature_extent_of_interest'),
            )

ef = EntityForm()

EntityMemberFormSet = inlineformset_factory(
    Entity,
    Person,
    form=EntityMemberForm,
    extra=1,
    )

emfs = EntityMemberFormSet()

EntityFormSet = formset_factory(EntityForm, extra=3)
entityform = EntityFormSet()

class NoteInlineForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Note
        exclude = ['user',]

class CommIndApplicationForm(forms.ModelForm):
    # Properties = forms.ModelMultipleChoiceField(
    #     queryset=Property.objects.all().order_by('street_address'),
    #     help_text='Select the property or properties you are applying for.',
    #     required=False
    # )

    status = forms.IntegerField(
        required=False
    )
    save_for_later = forms.CharField(required=False)

    entity_name = forms.CharField(required=False, help_text='Name of the entity that will take title, if known')
    entity_formed = forms.BooleanField(help_text='Has this entity already been formed?', label='Already formed?', required=False)
    entity_formed_date = forms.DateField(help_text='Date entity was formed, if applicable', required=False)
    entity_formed_location = forms.CharField(help_text='State or Country where entity was created', label='Formation', required=False)

    principal_1_name = forms.CharField(required=False, label='Name')
    principal_1_title = forms.CharField(required=False, label='Title')
    principal_1_email = forms.CharField(required=False, label='Email')
    principal_1_phone = forms.CharField(required=False, label='Phone')
    principal_1_address = forms.CharField(required=False, label='Mailing Address')
    principal_1_ownership_share = forms.CharField(required=False, label='Ownership Share', help_text='Percentage of entity controlled')

    principal_2_name = forms.CharField(required=False, label='Name')
    principal_2_title = forms.CharField(required=False, label='Title')
    principal_2_email = forms.CharField(required=False, label='Email')
    principal_2_phone = forms.CharField(required=False, label='Phone')
    principal_2_address = forms.CharField(required=False, label='Mailing Address')
    principal_2_ownership_share = forms.CharField(required=False, label='Ownership Share', help_text='Percentage of entity controlled')

    principal_3_name = forms.CharField(required=False, label='Name')
    principal_3_title = forms.CharField(required=False, label='Title')
    principal_3_email = forms.CharField(required=False, label='Email')
    principal_3_phone = forms.CharField(required=False, label='Phone')
    principal_3_address = forms.CharField(required=False, label='Mailing Address')
    principal_3_ownership_share = forms.CharField(required=False, label='Ownership Share', help_text='Percentage of entity controlled')

    principal_4_name = forms.CharField(required=False, label='Name')
    principal_4_title = forms.CharField(required=False, label='Title')
    principal_4_email = forms.CharField(required=False, label='Email')
    principal_4_phone = forms.CharField(required=False, label='Phone')
    principal_4_address = forms.CharField(required=False, label='Mailing Address')
    principal_4_ownership_share = forms.CharField(required=False, label='Ownership Share', help_text='Percentage of entity controlled')

    development_plan_file = forms.FileField(
        required=True,
        label='Development Plan',
        help_text='Please review <a href="/static/Development-Plan-2019-02-18.pdf">our template</a> as a reference point for what must be included',
    )
    # balance_sheet_file = forms.FileField(
    #     required=False,
    #     label='Balance Sheet',
    # )
    budget_and_financing_file = forms.FileField(
        required=True,
        label='Proof of Funds',
    )

    class Meta:
        model = Application
        exclude = ['user']

    def __init__(self, *args, **kwargs):
        #user = kwargs.pop('user')
        #app_id = kwargs.pop('id')

        super(CommIndApplicationForm, self).__init__(*args, **kwargs)
        self.fields['Property'].queryset = Property.objects.filter(status__exact=Property.AVAILABLE_STATUS)
        self.helper = FormHelper()
        self.helper.form_id = 'ApplicationForm'
        self.helper.form_class = 'form-horizontal'
        self.helper.field_class = 'col-lg-6'
        self.helper.label_class = 'col-lg-4'
        self.helper.render_unmentioned_fields = False #
        self.fields['applicant_skills_environmental_remediation'].widget = forms.Textarea(attrs={'rows': 4, 'cols': 25})
        self.fields['applicant_skills_brownfields'].widget = forms.Textarea(attrs={'rows': 4, 'cols': 25})
        self.fields['applicant_skills_commercial_real_estate_development'].widget = forms.Textarea(attrs={'rows': 4, 'cols': 25})
        self.fields['applicant_skills_entitlement_process'].widget = forms.Textarea(attrs={'rows': 4, 'cols': 25})
        self.fields['applicant_skills_incentives'].widget = forms.Textarea(attrs={'rows': 4, 'cols': 25})
        self.fields['applicant_skills_other'].widget = forms.Textarea(attrs={'rows': 4, 'cols': 25})
        self.fields['minority_owned_business_question_detail'].widget = forms.Textarea(attrs={'rows': 4, 'cols': 25})
        self.fields['arts_consideration_explanation'].widget = forms.Textarea(attrs={'rows': 4, 'cols': 25})
        self.fields['allignment_with_current_plans_details'].widget = forms.Textarea(attrs={'rows': 4, 'cols': 25})
        self.fields['stakeholders_contacted_details'].widget = forms.Textarea(attrs={'rows': 4, 'cols': 25})
        self.fields['existing_liens'].widget = forms.Textarea(attrs={'rows': 4, 'cols': 25})
        self.fields['entity_affiliates'].widget = forms.Textarea(attrs={'rows': 4, 'cols': 25})

        # for field in self.fields:
        #     if field

        self.helper.layout = Layout(
            Fieldset(
                'Commercial Land Bank Process Overview',
                HTML("""
                    <ol>
                    <li>Once application is complete, Renew Indianapolis will
                    begin the review process. If needed, Renew will contact the
                    Applicant for any missing documents and/or clarifications
                    regarding the application. </li>
                    <li>Registered neighborhood organizations will be contacted
                    for feedback on applications in their area. </li>
                    <li>Applications are presented to the Commercial Review
                    Committee bi-monthly. The committee deliberates and
                    approves or denies applications. </li>
                    <li>Approved applications will go before the Renew
                    Indianapolis Board for approval or denial on the first
                    Thursday of the month.</li>
                    <li>Board approved applications will go before the City's
                    Metropolitan Development Commission (MDC) for final
                    approval as a resolution. If the MDC approved the
                    application, the applicant/buyer is notified. The Buyer
                    must pay the processing fee and start the title search
                    with Fidelity National Title. Renew Indianapolis and DMD
                    will work closely with the Buyer to establish the project
                    agreement and move through the due diligence phase. From
                    application submission to closing, timing will vary
                    depending on the scope of the project. </li>
                    </ol>
                """),
                css_class='well'
            ),

            Fieldset(
                'Select a property',
                Div('Property'),
                css_class='well'
            ),
            Fieldset(
                'Applicant Disclosures',
                Field('conflict_renew_city'),
                Field('conflict_renew_city_name'),
                Field('existing_liens'),
                Field('active_citations'),
                Field('tax_status_of_properties_owned'),
                Field('prior_tax_foreclosure'),
                css_class='well'
            ),
            Fieldset(
                'Entity to Take Title',
                #Formset('EntityMemberForm'),
            #    HTML("""{{entity_form}} """),
#                Fieldset(
#                    'Entity',
#                    HTML(ef),
#                    HTML('{% crispy entity_form %}'),
#                    HTML(emfs),
#                ),
                Field('entity_name'),
                Field('entity_affiliates'),
                Field('entity_formed'),
                Field('entity_formed_date'),
                Field('entity_formed_location'),

                Fieldset(
                    'Principal #1',
                    Field('principal_1_name'),
                    Field('principal_1_title'),
                    Field('principal_1_email'),
                    Field('principal_1_phone'),
                    Field('principal_1_address'),
                    AppendedText('principal_1_ownership_share', '%'),
                    Button(
                        'cancel',
                        '+',
                        css_class='btn btn-default',
                        data_toggle='collapse',
                        data_target='#principal_2_id',
                        aria_expanded='false',
                        aria_controls='principal_2_id',
                        css_id='principal_1_button'
                    ), # The problem is that fundamentally I am a bad programmer.
                    HTML('<script>$("#principal_1_button").click(function(){$("#principal_1_button").addClass("hidden");})</script>'),
                ),
                Fieldset('Principal #2',
                    Field('principal_2_name'),
                    Field('principal_2_title'),
                    Field('principal_2_email'),
                    Field('principal_2_phone'),
                    Field('principal_2_address'),
                    AppendedText('principal_2_ownership_share', '%'),
                    Button(
                        'cancel',
                        '+',
                        css_class='btn btn-default',
                        data_toggle='collapse',
                        data_target='#principal_3_id',
                        aria_expanded='false',
                        aria_controls='principal_3_id',
                        css_id='principal_2_button',
                    ),
                    HTML('<script>$("#principal_2_button").click(function(){$("#principal_2_button").addClass("hidden");})</script>'),
                    css_class="collapse",
                    css_id='principal_2_id'
                ),
                Fieldset('Principal #3',
                    Field('principal_3_name'),
                    Field('principal_3_title'),
                    Field('principal_3_email'),
                    Field('principal_3_phone'),
                    Field('principal_3_address'),
                    AppendedText('principal_3_ownership_share', '%'),
                    Button(
                        'cancel',
                        '+',
                        css_class='btn btn-default',
                        data_toggle='collapse',
                        data_target='#principal_4_id',
                        aria_expanded='false',
                        aria_controls='principal_4_id',
                        css_id='principal_3_button',

                    ),
                    HTML('<script>$("#principal_3_button").click(function(){$("#principal_3_button").addClass("hidden");})</script>'),
                    css_class="collapse",
                    css_id='principal_3_id'
                ),
                Fieldset('Principal #4',
                    Field('principal_4_name'),
                    Field('principal_4_title'),
                    Field('principal_4_email'),
                    Field('principal_4_phone'),
                    Field('principal_4_address'),
                    AppendedText('principal_4_ownership_share', '%'),
                    css_class="collapse",
                    css_id='principal_4_id'
                ),
#                Button('cancel', 'Add another', css_class='btn btn-info'),
                css_class='well'

            ),
            Fieldset(
                'General Project Info',
                Field('project_type'),
                Field('allignment_with_current_plans'),
                Field('allignment_with_current_plans_details'),
                Field('stakeholders_contacted'),
                Field('stakeholders_contacted_details'),
                css_class='well',
            ),
            Fieldset(
                'Economics, Scope of Project &amp; Capacity',
                Field('applicant_offer_price'),
                Field('total_costs'),
                #Field('skills_and_expierence_applicant'),
                css_class='well'
            ),
            Fieldset(
                'Community Benefit &amp; Work Force',
                Field('total_number_of_jobs'),
                Field('total_annual_new_salaries'),
                Field('blended_hourly_wage_rate'),
                Field('hired_participant'),
                Field('low_mod_daycare'),
                Field('low_mod_transportation_support'),
                Field('youth_employment_opportunity'),
                Field('neighborhood_hiring_opportunity'),
                Field('subbaccalaureate_training_opportunity'),
                Field('arts_consideration'),
                Field('arts_consideration_explanation'),
                Field('minority_owned_business_question'),
                Field('minority_owned_business_question_detail'),
                css_class='well',
            ),
            Fieldset(
                'Skills and experience of the applicant that are relevant to this project',
                Div(
            #        'applicant_skills_environmental_remediation_boolean',#css_class='col-lg-3'),
                    'applicant_skills_environmental_remediation',# css_class='col-lg-9'),
                    class_class='row',
                ),
                Div(
            #        Field('applicant_skills_brownfields_boolean',css_class='col-lg-4'),
                    Field('applicant_skills_brownfields', css_class='col-lg-8'),
                    class_class='row',
                ),
                Div(
            #        Field('applicant_skills_commercial_real_estate_development_boolean',css_class='col-lg-4'),
                    Field('applicant_skills_commercial_real_estate_development', css_class='col-lg-8'),
                    class_class='row',
                ),
                Div(
            #        Field('applicant_skills_entitlement_process_boolean',css_class='col-lg-4'),
                    Field('applicant_skills_entitlement_process', css_class='col-lg-8'),
                    class_class='row',
                ),
                Div(
            #        Field('applicant_skills_incentives_boolean',css_class='col-lg-4'),
                    Field('applicant_skills_incentives', css_class='col-lg-8'),
                    class_class='row',
                ),
                Div(
            #        Field('applicant_skills_other_boolean',css_class='col-lg-4'),
                    Field('applicant_skills_other', css_class='col-lg-8'),
                    class_class='row',
                ),
                css_class='well',
            ),
            Fieldset(
                'Proof of Funds',
                HTML("""<p>
                    Please keep in mind that the guidelines below are a bare
                    minimum. We recommend providing proof of funds above the
                    project total noted in this application.</p>
                    <ol>
                    <li>All proposed new construction and rehabilitation
                    projects require 100% proof of funds for the total
                    project's costs. The following are acceptable forms of
                    proof of funds and should be attached to the
                    application:
                    <ul><li>Signed Balance sheet</li>
                    <li>Pre-Approval Letter from Lender</li>
                    <li>Proof of grant funding</li></ul>
                    </ol>
                    <p>Pre-approval letters from lenders' will require, if
                    the application is approved, a simultaneous closing
                    with the lender at the time of closing; or close on
                    the loan prior to closing.</p>
                """),
                #Field('source_of_financing'),
                Field('budget_and_financing_file'),
                css_class='well'
            ),
            Fieldset(
                'Development Plan',
                HTML("""<p>Before your application can be submitted for review
                    you must complete and attach a Development Plan and proof
                    of funds (see above for acceptable forms). Please attach
                    all above-mentioned files to this application when
                    submitting to Renew Indianapolis</p>
                    """),
                Field('development_plan_file'),
                css_class='well'),
            Fieldset(
                'General Notes',
                HTML("""
                    <ol>
                    <li>Within seven (7) days of final approval (the MDC for
                    city-owned properties and the board of Directors for
                    Renew-owned properties), Buyer(s) will submit a
                    non-refundable $500 processing fee.</li>
                    <li>The Sale will require a Project
                    Agreement which shall set forth the nature of any development
                    of the Property. The buyer shall execute such an agreement
                    with the Department of Metropolitan Development ("the DMD")
                    on behalf of Renew Indianapolis, within sixty (60) days of the
                    acceptance of the application. Renew Indianapolis and the
                    Applicant will work in tandem to determine the specifics of
                    the Project Agreement.</li>
                    <li>Environmental Regulatory Status - Buyer/Applicant will
                    be required to complete a Phase I prior to closing.</li>
                    </ol>
                """),
                css_class='well'
            ),
            FormActions(
                #Button('cancel', 'Cancel'),
    #            Submit('save_for_later', 'Save Application'),
                Submit('save', 'Validate and Submit Application'),
            )
        )
        self.helper.form_method = 'post'
        self.helper.form_action = ''

    def validate_for_submission(self, *args, **kwargs):
        #app_id = kwargs.pop('id')
        print("IN VALIDATE FOR SUBMISSION!!!!!!!!!!!")

        cleaned_data = super(CommIndApplicationForm, self).clean()
        conflict_renew_city = cleaned_data.get('conflict_renew_city', None)
        conflict_renew_city_name = cleaned_data.get(
            'conflict_renew_city_name', None)
        tax_status_of_properties_owned = cleaned_data.get(
            'tax_status_of_properties_owned', None)
        prior_tax_foreclosure = cleaned_data.get('prior_tax_foreclosure', None)
        active_citations = cleaned_data.get('active_citations', None)
        #planned_improvements = cleaned_data.get('planned_improvements')
        timeline = cleaned_data.get('timeline', None)
        estimated_cost = cleaned_data.get('estimated_cost', None)
        source_of_financing = cleaned_data.get('source_of_financing', None)

        property_selected = cleaned_data.get('Property', None)
        proof_of_funds = cleaned_data.get('proof_of_funds', None)
        total_number_of_jobs = cleaned_data.get('total_number_of_jobs', None)

        project_type = cleaned_data.get('project_type', None)
        if project_type is None:
            self.add_error("project_type", ValidationError(
                'This is a required question.'))

        allignment_with_current_plans = cleaned_data.get('allignment_with_current_plans', None)
        if allignment_with_current_plans is None:
            self.add_error("allignment_with_current_plans", ValidationError(
                'This is a required question.'))

        allignment_with_current_plans_details = cleaned_data.get('allignment_with_current_plans_details', None)
        if allignment_with_current_plans_details is None:
            self.add_error("allignment_with_current_plans_details", ValidationError(
                'This is a required question.'))

        stakeholders_contacted = cleaned_data.get('stakeholders_contacted', None)
        if stakeholders_contacted is None:
            self.add_error("stakeholders_contacted", ValidationError(
                'This is a required question.'))

        stakeholders_contacted_details = cleaned_data.get('stakeholders_contacted_details', None)
        if stakeholders_contacted_details is None or len(stakeholders_contacted_details) < 1:
            self.add_error("stakeholders_contacted_details", ValidationError(
                'You anwsered Yes above, please provide a name.'))

        applicant_skills_environmental_remediation = cleaned_data.get('applicant_skills_environmental_remediation', None)
        if applicant_skills_environmental_remediation is None:
            self.add_error("applicant_skills_environmental_remediation", ValidationError(
                'This is a required question.'))

        applicant_skills_brownfields = cleaned_data.get('applicant_skills_brownfields', None)
        if applicant_skills_brownfields is None:
            self.add_error("applicant_skills_brownfields", ValidationError(
                'This is a required question.'))

        applicant_skills_commercial_real_estate_development = cleaned_data.get('applicant_skills_commercial_real_estate_development', None)
        if applicant_skills_commercial_real_estate_development is None:
            self.add_error("applicant_skills_commercial_real_estate_development", ValidationError(
                'This is a required question.'))

        applicant_skills_entitlement_process = cleaned_data.get('applicant_skills_entitlement_process', None)
        if applicant_skills_entitlement_process is None:
            self.add_error("applicant_skills_entitlement_process", ValidationError(
                'This is a required question.'))

        applicant_skills_incentives = cleaned_data.get('applicant_skills_incentives', None)
        if applicant_skills_incentives is None:
            self.add_error("applicant_skills_incentives", ValidationError(
                'This is a required question.'))

        applicant_skills_other = cleaned_data.get('applicant_skills_other', None)
        if applicant_skills_other is None:
            self.add_error("applicant_skills_incentives", ValidationError(
                'This is a required question.'))


        if conflict_renew_city is None:
            self.add_error("conflict_renew_city", ValidationError(
                'This is a required question.'))

        if conflict_renew_city is True and conflict_renew_city_name == '':
            self.add_error("conflict_renew_city_name", ValidationError(
                "You anwsered Yes above, please provide a name."))

        if tax_status_of_properties_owned is None:
            self.add_error('tax_status_of_properties_owned',
                           ValidationError('This is a required question.'))

        if tax_status_of_properties_owned == Application.DELINQUENT_STATUS:
            self.add_error('tax_status_of_properties_owned', ValidationError(
                "Delinquent tax payers are not eligible to purchase properties from Renew Indianapolis"))

        if active_citations is None:
            self.add_error('active_citations', ValidationError(
                "This is a required question"))

        if prior_tax_foreclosure is None or prior_tax_foreclosure is True:
            self.add_error('prior_tax_foreclosure', ValidationError(
                "If you have previously lost a property in a tax foreclosure in Marion County you are not eligible to purchase properties from Renew Indianapolis."))

        if property_selected is None or property_selected == "":
            self.add_error('Properties', ValidationError(
                "You must select at least one property"))

        if total_number_of_jobs is None:
            self.add_error('total_number_of_jobs', ValidationError(
                "You must enter a number"))

        arts_consideration = cleaned_data.get('arts_consideration', None)
        arts_consideration_explanation = cleaned_data.get('arts_consideration_explanation', '')
        if arts_consideration is True and len(arts_consideration_explanation) < 1:
            self.add_error('arts_consideration_explanation', ValidationError(
                "You anwsered Yes above, please elaborate."))

        minority_owned_business_question = cleaned_data.get('minority_owned_business_question', None)
        minority_owned_business_question_detail = cleaned_data.get('minority_owned_business_question_detail', '')
        if minority_owned_business_question is True and len(minority_owned_business_question_detail) < 1:
            self.add_error('minority_owned_business_question_detail', ValidationError(
                "You anwsered Yes above, please elaborate."))


        return len(self.errors) == 0
