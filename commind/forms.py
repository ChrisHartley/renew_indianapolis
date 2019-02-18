from django import forms

from .models import Application, Property, Note, Entity, Document, Person
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder, Div, Button, MultiField, Field, HTML, Div, LayoutObject
from crispy_forms.bootstrap import FormActions, InlineRadios, PrependedAppendedText, InlineField, AppendedText
from django.core.urlresolvers import reverse
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

    entity = forms.ModelChoiceField(
        queryset=Entity.objects.all(),
        widget=AddAnotherWidgetWrapper(
            forms.Select(),
            Entity,
        ),
        help_text='If you are applying on behalf of an organization or another individual please add or select. <b>The property can only be titled under either your name or the name of an organization/individual included here..</b>',
        required=False
    )


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
    balance_sheet_file = forms.FileField(
        required=True,
        label='Balance Sheet',
    )
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
        self.helper = FormHelper()
        self.helper.form_id = 'ApplicationForm'
        self.helper.form_class = 'form-horizontal'
        self.helper.field_class = 'col-lg-6'
        self.helper.label_class = 'col-lg-4'
        self.helper.render_unmentioned_fields = False
        self.helper.layout = Layout(
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
            Fieldset(
                'Select a property',
                Div('Properties'),
                css_class='well'
            ),
            Fieldset(
                'Applicant Disclosures',
                Field('conflict_board_rc'),
                Field('conflict_board_rc_name'),
                Field('conflict_city'),
                Field('conflict_city_name'),
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
                ),
                Fieldset('Principal #2',
                    Field('principal_2_name'),
                    Field('principal_2_title'),
                    Field('principal_2_email'),
                    Field('principal_2_phone'),
                    Field('principal_2_address'),
                    AppendedText('principal_2_ownership_share', '%'),
                ),
                Fieldset('Principal #3',
                    Field('principal_3_name'),
                    Field('principal_3_title'),
                    Field('principal_3_email'),
                    Field('principal_3_phone'),
                    Field('principal_3_address'),
                    AppendedText('principal_3_ownership_share', '%'),
                ),
                Fieldset('Principal #4',
                    Field('principal_4_name'),
                    Field('principal_4_title'),
                    Field('principal_4_email'),
                    Field('principal_4_phone'),
                    Field('principal_4_address'),
                    AppendedText('principal_4_ownership_share', '%'),
                ),
#                Button('cancel', 'Add another', css_class='btn btn-info'),
                css_class='well'

            ),

            Fieldset(
                'Applicant Questions',
                Field('applicant_work_character'),
                Field('applicant_experience'),
                Field('applicant_brownfield_experience'),
                #Field('applicant_similar_experience'),
                Field('applicant_joint_venture'),
                Field('applicant_partnerships'),
                css_class='well',
            ),
            Fieldset(
                'Project Description',
                Field('applicant_offer_price'),
                Field('proposed_end_use'),
                css_class='well'
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
                    you must complete and attach a
                    Development Plan and proof of funds (see above for acceptable forms).
                    Please attach all above-mentioned files to this application
                    when submitting to Renew Indianapolis</p>
                    <p>A template for the Development Plan is <a href="/static/Development-Plan-2019-02-18.pdf">available here.</a></p>

                    """),
                Field('development_plan_file'),
#                Field('balance_sheet_file'),
#                Field('budget_and_financing_file'),
                #HTML('<div class="form-group"><div class="control-label col-lg-4">Applicant Qualifiction &amp; Development Plan</div><div id="developmentplan-file-uploader" class="form-control-static col-lg-6">Drop your scope of work file here to upload</div>'),
                #HTML('<div class="help-block col-lg-6 col-lg-offset-4">Please review our <a href="http://build.renewindianapolis.org/static/Scope-of-Work-Template.xls" target="_blank">template</a> as a reference point for what must be included.</div></div>'),

                #HTML('<div class="form-group"><div class="control-label col-lg-4">Balance Sheet</div><div id="balancesheet-file-uploader" class="form-control-static col-lg-6">Drop your balance sheet file here to upload</div></div>'),

                #HTML('<div class="form-group"><div class="control-label col-lg-4">Budget and Finacing</div><div id="budget-file-uploader" class="form-control-static col-lg-6">Drop your balance sheet file here to upload</div></div>'),

                #HTML('<p>To delete an uploaded file, click "Save Application", then scroll down and click the red "X" after the file name.</p>'),

                #HTML("""<p>Previously uploaded files:<ul>
                #        {% for file in uploaded_files_all %}
                #            <li>{{ file }} <img src="{{STATIC_URL}}admin/img/icon-deletelink.svg" id='uploadedfile_{{ file.id }}' class='uploaded_file_delete' alt='[X]'></img></li>
                #            {% empty %}
                #                <li>No files are associated with this application.</li>
                #        {% endfor%}
                #        </ul>
                #    </p>"""),
                    css_class='well'),
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
        cleaned_data = super(CommIndApplicationForm, self).clean()
        conflict_board_rc = cleaned_data.get('conflict_board_rc', None)
        conflict_board_rc_name = cleaned_data.get(
            'conflict_board_rc_name', None)
        conflict_city = cleaned_data.get('conflict_city', None)
        conflict_city_name = cleaned_data.get(
            'conflict_city_name', None)
        tax_status_of_properties_owned = cleaned_data.get(
            'tax_status_of_properties_owned', None)
        prior_tax_foreclosure = cleaned_data.get('prior_tax_foreclosure', None)
        active_citations = cleaned_data.get('active_citations', None)

        #planned_improvements = cleaned_data.get('planned_improvements')
        timeline = cleaned_data.get('timeline')
        estimated_cost = cleaned_data.get('estimated_cost')
        source_of_financing = cleaned_data.get('source_of_financing')

        properties_selected = cleaned_data.get('Properties')
        proof_of_funds = cleaned_data.get('proof_of_funds')


        if conflict_board_rc is None:
            self.add_error("conflict_board_rc", ValidationError(
                'This is a required question.'))

        if conflict_board_rc is True and conflict_board_rc_name == '':
            self.add_error("conflict_board_rc_name", ValidationError(
                "You anwsered Yes above, please provide a name."))

        if conflict_city is None:
            self.add_error("conflict_city", ValidationError(
                'This is a required question.'))

        if conflict_city is True and conflict_city_name == '':
            self.add_error("conflict_city_name", ValidationError(
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

        if properties_selected is None or properties_selected == "":
            self.add_error('Properties', ValidationError(
                "You must select at least one property"))

        print self.errors
        return len(self.errors) == 0
