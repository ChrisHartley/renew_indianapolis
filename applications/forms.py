from django import forms
from django.core.urlresolvers import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder, Div, Button, MultiField, Field, HTML, Div
from crispy_forms.bootstrap import FormActions, InlineRadios, PrependedAppendedText, InlineField
from user_files.models import UploadedFile
from .models import Application, MeetingLink, Meeting
from property_inventory.models import Property
from applicants.models import Organization
from django.forms.models import inlineformset_factory
from applicants.widgets import AddAnotherWidgetWrapper
from django.core.exceptions import ValidationError
from django.contrib.admin.widgets import ForeignKeyRawIdWidget

class ScheduleInlineForm(forms.Form):
    meeting = forms.ModelChoiceField(Meeting.objects.all().order_by('-meeting_date') )
    meeting_outcome = forms.ChoiceField(choices=MeetingLink.STATUS_CHOICES, initial=MeetingLink.SCHEDULED_STATUS)

class ApplicationForm(forms.ModelForm):
    Property = forms.ModelChoiceField(
        queryset=Property.objects.exclude(status__contains='Sale approved by MDC').exclude(is_active__exact=False).exclude(
            status__contains='Sold').exclude(status__contains='BEP').exclude(status__contains='Sale approved by Board of Directors', renew_owned=True).order_by('streetAddress'),
        help_text='Select the property you are applying for. One property per application.',
        required=False
    )
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.all(),
        widget=AddAnotherWidgetWrapper(
            forms.Select(),
            Organization,
        ),
        help_text='If you are applying on behalf of an organization or another individual please add or select. <b>The property can only be titled under either your name or the name of an organization/individual included here..</b>',
        required=False
    )
    status = forms.IntegerField(
        required=False
    )
    save_for_later = forms.CharField(required=False)

    class Meta:
        model = Application
        exclude = ['user']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        app_id = kwargs.pop('id')
        super(ApplicationForm, self).__init__(*args, **kwargs)
        self.fields['organization'].queryset = Organization.objects.filter(
            user=user).order_by('name')

        valid_application_types = ((None, '---------'),)
        for app_type,description in Application.APPLICATION_TYPES:
            if app_type in Application.ACTIVE_APPLICATION_TYPES:
                valid_application_types = valid_application_types + ((app_type,description),)
        self.fields['application_type'].choices = valid_application_types

        self.helper = FormHelper()
        self.helper.form_id = 'ApplicationForm'
        self.helper.form_class = 'form-horizontal'
        self.helper.field_class = 'col-lg-6'
        self.helper.label_class = 'col-lg-4'
        self.helper.render_unmentioned_fields = False
        self.helper.layout = Layout(
            Fieldset(
                'About You',
                Field('conflict_board_rc'),
                Field('conflict_board_rc_name'),
                Field('conflict_city'),
                Field('conflict_city_name'),
                Field('active_citations'),
                Field('tax_status_of_properties_owned'),
                Field('other_properties_names_owned'),
                Field('prior_tax_foreclosure'),
                Field('landlord_in_marion_county'),
                Field('landlord_registry'),
                Field('organization'),
                HTML('<div class="form-group"><div class="control-label col-lg-4">Third Party Authorization Form</div><div id="3rd-party-authorization-file-uploader" class="form-control-static col-lg-6">Drop your third party authorization form file here to upload</div>'),
                HTML("""<div class="help-block col-lg-6 col-lg-offset-4">
                            If someone is completing this application on your behalf, such as a Realtor&trade;, a translator, a family member, or a friend then you and they will need to complete
                            a <a href="https://build.renewindianapolis.org/static/Third-Party-Authorization.pdf" target="_blank">Third Party Authorization Form (pdf)</a> and upload the completed, signed form here.
                            </div>
                        """),

                css_class='well'
            ),
            Fieldset(
                'Select a property',
                Div('Property'),
                HTML('<div class="form-group"><div class="control-label col-lg-4">Status: </div><div id="status" class="col-lg-6 form-control-static"></div></div>'),
                HTML('<div class="form-group"><div class="control-label col-lg-4">Structure Type: </div><div id="structureType" class="form-control-static col-lg-6"></div></div>'),
                HTML('<div class="form-group"><div class="control-label col-lg-4">Sidelot Eligible: </div><div id="sidelot_eligible" class="form-control-static col-lg-6"></div></div>'),
                HTML('<div class="form-group"><div class="control-label col-lg-4">Vacant Lot Eligible: </div><div id="vacant_lot_eligible" class="form-control-static col-lg-6"></div></div>'),
                HTML('<div class="form-group"><div class="control-label col-lg-4">Future Development Lot Sales Program Eligible: </div><div id="fdl_eligible" class="form-control-static col-lg-6"></div></div>'),
                HTML('<div class="form-group"><div class="control-label col-lg-4">Price: </div><div id="price" class="form-control-static col-lg-6"></div></div>'),
                HTML('<div class="form-group"><div class="control-label col-lg-4">Homestead Only: </div><div id="homestead_only" class="form-control-static col-lg-6"></div></div>'),
                HTML('<div class="form-group"><div class="control-label col-lg-4">Blight Elimination Program (demolition): </div><div id="bep_property" class="form-control-static col-lg-6"></div></div>'),
                css_class='well'
            ),
            Fieldset(
                'Application Type',
                Div('application_type'),
                HTML('<div id="homestead_only_warning" class="panel panel-danger" style="display:none"><div class="panel-heading"><h3 class="panel-title">Homesead Only</h3></div><div class="panel-body">The property you selected is only available for homestead (owner occupant) applications.</div></div>'),
                HTML('<div id="bep_explanation" class="panel panel-warning" style="display:none"><div class="panel-heading"><h3 class="panel-title">Blight Elimination Program Sidelot Moratorium</h3></div><div class="panel-body">This property is owned by Renew Indianapolis through the Blight Elimination Program. The Renew Indianapolis Board of Directors decided at their September 7th, 2017 program to put a temporary moratorium on the sale of BEP lots through the sidelot program. Please check back for an update on this program.</div></div>'),
                css_class='well'
            ),
            Fieldset(
                'Ownership and Use',
                Field('long_term_ownership'),
                Field('is_rental'),
                css_class='standard-app well'
            ),
            Fieldset(
                'Planned Improvements',
                Field('planned_improvements'),
                Field('finished_square_footage'),
                Field('timeline'),
                css_class='standard-app homestead-app well'
            ),
            Fieldset(
                'Budget and Funding',
                Field(PrependedAppendedText('estimated_cost', '$', '.00')),
                Field('source_of_financing'),
                css_class='standard-app homestead-app well'
            ),
            Fieldset(
                'Sidelot Eligiblity',
                Field('sidelot_eligible'),
                css_class='sidelot-app well'
            ),
            # Fieldset(
            #     'Vacant Lot End Use',
            #     Field('vacant_lot_end_use'),
            #     css_class='vacantlot-app well'
            # ),
            Fieldset(
                'Future Development Lot Application Questions',
                Field('vacant_lot_end_use'),
                css_class='fdl-app well'
            ),

            Fieldset(
                'Uploaded Files',
                HTML('<p>Before your application can be submitted for review you must attach both a scope of work and proof of funds, as referenced earlier. You can upload those files here.</p>'),

                HTML('<div class="form-group"><div class="control-label col-lg-4">Scope of Work</div><div id="sow-file-uploader" class="form-control-static col-lg-6">Drop your scope of work file here to upload</div>'),
                HTML('<div class="help-block col-lg-6 col-lg-offset-4">We highly recommend using our <a href="http://build.renewindianapolis.org/static/Scope-of-Work-Template.xls" target="_blank">spreadsheet</a> or <a href="https://build.renewindianapolis.org/static/Scope-of-Work-Template.pdf" target="_blank">printable template</a> as a starting point.</div></div>'),

                HTML('<div class="form-group"><div class="control-label col-lg-4">Elevation View</div><div id="elevation-file-uploader" class="form-control-static col-lg-6">Drop your elevation view file here to upload</div></div>'),

                HTML('<div class="form-group"><div class="control-label col-lg-4">Site Plan</div><div id="siteplan-file-uploader" class="form-control-static col-lg-6">Drop your site plan file here to upload</div></div>'),

                HTML('<div class="form-group"><div class="control-label col-lg-4">Floor Plan</div><div id="floorplan-file-uploader" class="form-control-static col-lg-6">Drop your floor plan file here to upload</div>'),
                HTML('<div class="help-block col-lg-6 col-lg-offset-4">If you are proposing new construction on a vacant lot you must upload an site plan, elevation view and floor plan of your proposed construction.</div></div>'),

                HTML('<div class="form-group"><div class="control-label col-lg-4">Proof of Funds</div><div id="pof-file-uploader" class="form-control-static col-lg-6">Drop your proof of funds file here to upload</div>'),
                HTML("""<div class="help-block col-lg-6 col-lg-offset-4">
                            Upload documents demonstrating your plan to pay for your proposed improvements as outlined
                            in the "Budgeting and Financing" section. Examples include: a bank statement, a completed
                            and notarized affidavit, pre-approval letter from a lender, etc
                            <ol>
                            <li>Rehabilitation projects, including homes for rental or for sale projects, must
                                show acceptable proof of funds for 75-100% of the total project costs less any
                                materials on hand.  An <a href="https://build.renewindianapolis.org/static/Affidavit-self.pdf" target="_blank">affidavit of funds</a> (PDF) may be used for up to 25% of the total
                                project costs.</li>
                            <li>Homestead (owner occupied) rehabilitation projects may demonstrate 100% of funds through an
                                <a href="https://build.renewindianapolis.org/static/Affidavit-self.pdf" target="_blank">affidavit of funds</a> (PDF).</li>

                            <li>All proposed new construction projects require proof of funds for 75% of the
                                total project costs.  An <a href="https://build.renewindianapolis.org/static/Affidavit-self.pdf" target="_blank">affidavit of funds</a> (PDF) may be used for up to 25% of the total
                                project costs.</li>
                            </ol></div></div>"""
                     ),
                HTML('<p>To delete an uploaded file, click "Save Application", then scroll down and click the red "X" after the file name.</p>'),

                HTML("""<p>Previously uploaded files:<ul>
                        {% for file in uploaded_files_all %}
                            <li>{{ file }} <img src="{{STATIC_URL}}admin/img/icon-deletelink.svg" id='uploadedfile_{{ file.id }}' class='uploaded_file_delete' alt='[X]'></img></li>
                            {% empty %}
                                <li>No files are associated with this application.</li>
                        {% endfor%}
                        </ul>
                    </p>"""),
                css_class='standard-app homestead-app well'),
            FormActions(
                #Button('cancel', 'Cancel'),
                Submit('save_for_later', 'Save Application'),
                Submit('save', 'Validate and Submit Application'),
            )
        )
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('process_application', kwargs={
                                          'action': 'save', 'id': app_id})

    def validate_for_submission(self, *args, **kwargs):
        app_id = kwargs.pop('id')
        cleaned_data = super(ApplicationForm, self).clean()
        application_type = cleaned_data.get('application_type', None)
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
        landlord_in_marion_county = cleaned_data.get('landlord_in_marion_county', None)
        landlord_registry = cleaned_data.get('landlord_registry', None)

        planned_improvements = cleaned_data.get('planned_improvements')
        timeline = cleaned_data.get('timeline')
        estimated_cost = cleaned_data.get('estimated_cost')
        source_of_financing = cleaned_data.get('source_of_financing')

        long_term_ownership = cleaned_data.get('long_term_ownership')
        is_rental = cleaned_data.get('is_rental')
        property_selected = cleaned_data.get('Property')
        proof_of_funds = cleaned_data.get('proof_of_funds')
        sidelot_eligible = cleaned_data.get('sidelot_eligible', None)
        square_footage = cleaned_data.get('finished_square_footage')
        vacant_lot_end_use = cleaned_data.get('vacant_lot_end_use', None)


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

        if landlord_in_marion_county is None:
            self.add_error('landlord_in_marion_county', ValidationError(
                "This is a required question."))

        if landlord_registry is None:
            self.add_error('landlord_registry', ValidationError(
                "This is a required question. Select Not Applicable if you do not own any rental properties."))

        if landlord_in_marion_county is True and (landlord_registry is None or landlord_registry == Application.NA_YNNA_CHOICE):
            self.add_error('landlord_registry', ValidationError(
                "You answered Yes above, please answer Yes or No to this question."))

        if landlord_in_marion_county is False and landlord_registry != Application.NA_YNNA_CHOICE:
            self.add_error('landlord_registry', ValidationError(
                "You answered that you do not own any rental properties above so your answer should be Not Applicable"))

        if landlord_in_marion_county is True and landlord_registry == Application.NO_YNNA_CHOICE:
            self.add_error('landlord_registry', ValidationError(
                "Rental properties in Marion County must be properly registered in the Landlord Registry before you can submit an application to Renew Indianapolis."))


        if property_selected is None or property_selected == "":
            self.add_error('Property', ValidationError(
                "You must select a property"))

        if application_type is None or application_type == "":
            self.add_error('application_type', ValidationError(
                "You must select an application type"))

        if Application.SIDELOT == application_type:
            msg = "This is a required question."
            if sidelot_eligible is None:
                self.add_error('sidelot_eligible', ValidationError(msg))
            if property_selected is not None and property_selected.structureType != "Vacant Lot":
                self.add_error('application_type', ValidationError(
                    'The property you have selected is not a vacant lot and hence is ineligible for our sidelot program.'))
            if property_selected is not None and property_selected.hhf_demolition == True:
                self.add_error('application_type', ValidationError(
                    'This property is a BEP property and as such is not currently eligible for sale through our sidelot program.'
                ))

        if Application.VACANT_LOT == application_type:
            if property_selected is not None and property_selected.structureType != "Vacant Lot":
                self.add_error('application_type', ValidationError(
                    'The property you have selected is not a vacant lot and hence is ineligible for our vacant lot program.'))
            else:
                if property_selected is not None and property_selected.vacant_lot_eligible != True:
                    self.add_error('application_type', ValidationError(
                    """
                        The property you have selected is not eligible for the
                        vacant lot program. Properties in some locations are
                        not eligible for sale under the vacant lot program.
                        These properties are available for development under our
                        standard or homestead programs.
                        """))
                else:
                    if vacant_lot_end_use == '':
                        self.add_error('vacant_lot_end_use', ValidationError(
                        'Please answer this question.'
                        ))

        if Application.FDL == application_type:
            if property_selected is not None and property_selected.structureType != "Vacant Lot":
                self.add_error('application_type', ValidationError(
                    'The property you have selected is not a vacant lot and hence is ineligible for our future development lot sales program.'))
            else:
                if property_selected is not None and property_selected.future_development_program_eligible != True:
                    self.add_error('application_type', ValidationError(
                    """
                        The property you have selected is not eligible for the
                        Future Development Lot (FDL) sales program. Properties in
                        some locations are not eligible for sale under the
                        Future Development Lot (FDL) sales program.
                        These properties are available for development under our
                        standard or homestead programs."""
                        ))
                else:
                    pass

        if Application.HOMESTEAD == application_type or Application.STANDARD == application_type:
            msg = "This is a required field."
            if not planned_improvements or planned_improvements == "":
                self.add_error('planned_improvements', ValidationError(msg))
            if not timeline or timeline == "":
                self.add_error('timeline', ValidationError(msg))
            if property_selected is not None and property_selected.structureType == "Vacant Lot" and (not square_footage or square_footage == ""):
                self.add_error('finished_square_footage', ValidationError(msg))
            if not estimated_cost or estimated_cost == 0:
                self.add_error('estimated_cost', ValidationError(msg))
            if not source_of_financing or source_of_financing == "":
                self.add_error('source_of_financing', ValidationError(msg))
            if UploadedFile.objects.filter(file_purpose__exact=UploadedFile.PURPOSE_SOW).filter(application__exact=app_id).count() == 0:
                self.add_error(None, ValidationError(
                    'You must upload a separate scope of work document with your application.'))
            if UploadedFile.objects.filter(file_purpose__exact=UploadedFile.PURPOSE_POF).filter(application__exact=app_id).count() == 0:
                self.add_error(None, ValidationError(
                    'You must upload a separate proof of funds document with your application.'))
            if UploadedFile.objects.filter(file_purpose__exact=UploadedFile.PURPOSE_SITE_PLAN).filter(application__exact=app_id).count() == 0 and property_selected is not None and property_selected.structureType == "Vacant Lot":
                self.add_error(None, ValidationError(
                    'You must upload a separate site plan with your application since the selected property is a vacant lot.'))
            if UploadedFile.objects.filter(file_purpose__exact=UploadedFile.PURPOSE_FLOOR_PLAN).filter(application__exact=app_id).count() == 0 and property_selected is not None and property_selected.structureType == "Vacant Lot":
                self.add_error(None, ValidationError(
                    'You must upload a separate floor plan with your application since the selected property is a vacant lot.'))
            if UploadedFile.objects.filter(file_purpose__exact=UploadedFile.PURPOSE_ELEVATION_VIEW).filter(application__exact=app_id).count() == 0 and property_selected is not None and property_selected.structureType == "Vacant Lot":
                self.add_error(None, ValidationError(
                    'You must upload a separate elevation view with your application since the selected property is a vacant lot.'))



            if Application.STANDARD == application_type:
                if not long_term_ownership or long_term_ownership == "":
                    self.add_error('long_term_ownership', ValidationError(msg))
                if is_rental is None:  # boolean value
                    self.add_error('is_rental', ValidationError(msg))
                #if is_rental and property_selected and property_selected.nsp and nsp_income_qualifier == "":
                #    self.add_error('nsp_income_qualifier', ValidationError(
                #        "Since this is a rental NSP property you must list who will be conducting tenant income qualification."))
                #if is_rental and property_selected and property_selected.nsp:
                #    self.add_error('is_rental', ValidationError(
                #        "Per City of Indianapolis policy, NSP properties may not be used as rental properties."))
                if property_selected is not None and property_selected.homestead_only:
                   self.add_error('application_type', ValidationError(
                       'The property you have selected is marked "homestead only" but you indicated a Standard application. This property can only be sold to an owner occupant.'))

        return len(self.errors) == 0
