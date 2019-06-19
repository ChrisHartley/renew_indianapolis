from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic.base import TemplateView, RedirectView
from django.views.static import serve
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required

from applications.views import ApplicationDetail, ApplicationDisplay, ApplicationNeighborhoodNotification, ApplicationPurchaseAgreement, ReviewCommitteeAgenda, ReviewCommitteeStaffSummary, CreateMeetingSupportArchive, ReviewCommitteeApplications, application_confirmation, process_application, PriceChangeSummaryAll, CreateMeetingPriceChangeCMAArchive, MeetingOutcomeNotificationSpreadsheet, ePPPropertyUpdate, ePPPartyUpdate, GenerateNeighborhoodNotifications, GenerateNeighborhoodNotificationsVersion2, MDCResolution
from photos.views import DumpPhotosView, PropertyPhotosView
from property_inventory.views import PropertyDetailView, getAddressFromParcel, showApplications, get_inventory_csv, searchProperties, propertyPopup, PropertyDetailJSONView, InventoryMapTemplateView, ContextAreaListJSONView, PriceChangeSummaryView, get_featured_properties_csv, SlimPropertySearchView
from property_inventory.views import PropertyInventoryList
from property_inquiry.views import property_inquiry_confirmation, submitPropertyInquiry, CreateIcsFromShowing, propertyShowingReleaseView, propertyShowingListEmailTemplateView
from applicants.views import edit_organization, profile_home, profile_home, showApplicantProfileForm, show_organizations
from surplus.views import ParcelDetailView, ParcelDetailView, ParcelListView, SurplusMapTemplateView, ParcelUpdateView, surplusUpdateFieldsFromMap, searchSurplusProperties, get_surplus_inventory_csv
from annual_report_form.views import showAnnualReportForm
from user_files.views import delete_uploaded_file, import_uploader
from closings.views import ProcessingFeePaymentPage, ProcessingFeePaidPage, ClosingDepositSlipDetailView
from property_condition.views import submitConditionReport, view_or_create_condition_report
from univiewer.views import UniPropertySearchView, UniParcelDetailJSONView, UniMapTemplateView, UniParcelUpdateView, bepUpdateFieldsFromMap, get_uniinventory_csv
from epp_connector.views import fetch_epp_inventory, propertyImportCreator
from neighborhood_notifications.views import update_registered_organizations, RelevantOrganizationsView
#from post_sale.views import ApplicationModifyProjectAggreementCreate, ApplicationModifyProjectAggreementUpdate
from utils.views import DonateView, send_class_file
from commind.views import view_document, CommIndApplicationFormView, PropertyListView, CommIndApplicationSuccessView, CommIndApplicationDetailView

admin.site.site_header = 'Blight Fight administration'
from django.conf.urls import url  # For django versions before 2.0
urlpatterns = [
        url(r'admin/', admin.site.urls),
        url(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
        url(r'^$', profile_home,
           name='applicants_home'),

        url(r'lookup_street_address/$', getAddressFromParcel,
           name='get_address_from_parcel'),

        url(r'property_inquiry/thanks/(?P<id>[0-9]+)$',
           property_inquiry_confirmation, name='property_inquiry_confirmation'),
        url(r'property_inquiry/$', submitPropertyInquiry,
           name='submit_property_inquiry'),

        url(r'property_inquiry/create_ics/(?P<pks>(\d+(,\d+)*))/$', CreateIcsFromShowing.as_view(),
           name='property_inquiry_create_showing_ics'),
        url(r'property_inquiry/showing_emails/(?P<pks>(\d+(,\d+)*))/$', propertyShowingListEmailTemplateView.as_view(),
           name='property_inquiry_showing_emails'),
        url(r'property_inquiry/release_template/(?P<pks>(\d+(,\d+)*))/$', propertyShowingReleaseView.as_view(),
           name='property_inquiry_showing_release'),

        url(r'search-neighborhood-association/(?P<parcel>[0-9]{7})/$',
           RelevantOrganizationsView.as_view()),

        url(r'application_status/$',
           showApplications, name="application_status"),
        url(r'show/search/$', get_inventory_csv, name='inventory_download'),
        #url(r'show/mdc_download/$', 'property_inventory.views.get_mdc_csv', name='mdc_download'),
        url(r'show/search/featured/$', get_featured_properties_csv, name='featured_inventory_download' ),


        url(r'search_property/$',
           searchProperties, name='search_property'),
        url(r'search-map/$',
           searchProperties),


        url(r'surplus/$', SurplusMapTemplateView.as_view(), name='surplus_map'),
        url(r'surplus/search/$', searchSurplusProperties, name='surplus_search'),
        url(r'surplus/property/(?P<parcel>[0-9]{7})/$', ParcelDetailView.as_view(), name='surplus_property'),
        url(r'surplus/property/update/$', surplusUpdateFieldsFromMap, name='surplus_property_update'),
        url(r'surplus/property/update/(?P<parcel>[0-9]{7})/$', ParcelUpdateView.as_view(), name='surplus_property_update_parcel'),
        url(r'surplus/download/$', get_surplus_inventory_csv, name='surplus_download_csv'),


        url(r'propertyPopup/$',
           propertyPopup),

        url(r'property/map/$', InventoryMapTemplateView.as_view(), name='property_map'),
        url(r'property/search/$', SlimPropertySearchView.as_view(), name='property_search'),
        url(r'property/(?P<parcel>[0-9]{7})/$',
            PropertyDetailView.as_view(), name='property_view'),
        url(r'property/(?P<parcel>[0-9]{7}),(?P<address>[-\w|\W|\d]+)/$',
            PropertyDetailView.as_view(), name='property_view_slug'),

        url(r'property/(?P<parcel>[0-9]{7})/photos/$',
            PropertyPhotosView.as_view(), name='property_photos'),
        url(r'property/(?P<parcel>[0-9]{7})/json$',
            PropertyDetailJSONView.as_view(), name='property_detail_json'),
        url(r'property/(?P<parcel>[0-9]{7})/epp.xlsx$',
                staff_member_required(propertyImportCreator.as_view()), name='property_export_epp'),

        url(r'overlay_area/context_areas/$', ContextAreaListJSONView.as_view(), name='overlay_area'),

        url(r'annual-report/$',
           showAnnualReportForm),

        url(r'admin_add_photos/$', staff_member_required(DumpPhotosView.as_view()), name="admin_add_photos"),

        url(r'accounts/profile$', profile_home,
           name='applicants_home'),
        url(r'accounts/profile/edit$',
           showApplicantProfileForm, name='applicants_profile'),
        url(r'accounts/organization/new/$', login_required(edit_organization.as_view()),
           name='applicants_organization_add'),
        url(r'accounts/organization/edit/(?P<id>\w+)/$',
           login_required(edit_organization.as_view()), name='applicants_organization_edit'),
        url(r'accounts/organization$', show_organizations,
           name='applicants_organization'),

        # django all-auth
        url(r'accounts/', include('allauth.urls')),

        url(r'utils/delete_file/$',
           delete_uploaded_file, name='uploadedfile_delete'),
        url(r'utils/upload_file/$',
           import_uploader, name='my_ajax_upload'),

        url(r'application/thanks/(?P<id>[0-9]+)$',
           application_confirmation, name='application_confirmation'),

        url(r'application/view/(?P<pk>[0-9]+)/$', staff_member_required(ApplicationDetail.as_view()), name="application_summary_page"),
        url(r'application/view/complete/(?P<pk>[0-9]+)/$', staff_member_required(ApplicationDisplay.as_view()), name="application_detail_page"),
        url(r'application/view/neighborhood/(?P<pk>[0-9]+)/$',
            staff_member_required(ApplicationNeighborhoodNotification.as_view()),
            name='application_neighborhood_notification'),
        url(r'application/view/purchase_agreement/(?P<pk>[0-9]+)/$',
            staff_member_required(ApplicationPurchaseAgreement.as_view()),
            name='application_purchase_agreement'),
        url(r'application/processing_fee/(?P<slug>[-\w\d]+),(?P<id>[-\w\d]+)/$',
            login_required(ProcessingFeePaymentPage.as_view()),
            name='application_pay_processing_fee'
        ),
        url(r'application/processing_fee/(?P<slug>[-\w\d]+),(?P<id>[-\w\d]+)/paid$',
            login_required(ProcessingFeePaidPage.as_view()),
            name='application_paid_processing_fee'
        ),

        # url(r'application/modify_project_aggreement/(?P<pk>[0-9]+)/$',
        #     login_required(ApplicationModifyProjectAggreementUpdate.as_view()),
        #     name='modify_project_aggreement_edit_application'),
        #
        # url(r'application/modify_project_aggreement/new/$',
        #     login_required(ApplicationModifyProjectAggreementCreate.as_view()),
        #     name='modify_project_aggreement_new_application'),


        url(r'meeting/view_agenda/(?P<pk>[0-9]+)/$',
             staff_member_required(ReviewCommitteeAgenda.as_view()),
             name='rc_agenda'),
        url(r'meeting/view_mdc_resolution/(?P<pk>[0-9]+)/$',
             staff_member_required(MDCResolution.as_view()),
             name='mdc_resolution'),
        url(r'meeting/view_packet/(?P<pk>[0-9]+)/$',
            staff_member_required(ReviewCommitteeStaffSummary.as_view()),
            name='staff_packet'),
        url(r'meeting/view_packet/applications/(?P<pk>[0-9]+)/$',
            staff_member_required(ReviewCommitteeApplications.as_view()),
            name='application_packet'),

        url(r'meeting/view_packet_attachement/(?P<pk>[0-9]+)/$',
             staff_member_required(CreateMeetingSupportArchive.as_view()),
             name='staff_packet_attachements'),

        url(r'meeting/epp_update_spreadsheet/(?P<pk>[0-9]+)/$',
             staff_member_required(ePPPropertyUpdate.as_view()),
             name='epp_update_spreadsheet'),

        url(r'meeting/epp_update_party_spreadsheet/(?P<pk>[0-9]+)/$',
             staff_member_required(ePPPartyUpdate.as_view()),
             name='epp_update_party_spreadsheet'),


        url(r'meeting/mail_merge_notification_spreadsheet/(?P<pk>[0-9]+)/$',
             staff_member_required(MeetingOutcomeNotificationSpreadsheet.as_view()),
             name='meeting_outcome_notification_spreadsheet'),

        url(r'meeting/generate_neighborhood_notifications/(?P<pk>[0-9]+)/$',
            staff_member_required(GenerateNeighborhoodNotifications.as_view()),
            name='generate_neighborhood_notifications'),

        url(r'meeting/generate_neighborhood_notifications2/(?P<pk>[0-9]+)/$',
            staff_member_required(GenerateNeighborhoodNotificationsVersion2.as_view()),
            name='generate_neighborhood_notifications2'),

        url(r'meeting/price_change/view_packet/(?P<pk>[0-9]+)/$',
            staff_member_required(PriceChangeSummaryAll.as_view()),
            name='price_change_summary_view_all'),
        url(r'meeting/price_change/view_packet_attachement/(?P<pk>[0-9]+)/$',
             staff_member_required(CreateMeetingPriceChangeCMAArchive.as_view()),
             name='staff_packet_price_change_CMA_attachements'),


        url(r'meeting/price_change/(?P<pk>[0-9]+)/$',
            staff_member_required(PriceChangeSummaryView.as_view()),
            name='price_change_summary_view'),

        url(r'^application/(?P<action>\w+)/$',
           process_application, name='process_application'),
        url(r'application/(?P<action>\w+)/(?P<id>[0-9]+)/$',
           process_application, name='process_application'),

#from uniview.views import UniPropertySearchView, UniParcelDetailJSONView, UniMapTemplateView


        url(r'inventory_review/search/$',
            staff_member_required(UniPropertySearchView.as_view()),
            name='inventory_review_search'),
        url(r'inventory_review/parcel/(?P<parcel>[0-9]{7})/json$',
            staff_member_required(UniParcelDetailJSONView.as_view()),
            name='inventory_review_parcel_json'),
        url(r'inventory_review/parcel/update/$',
            bepUpdateFieldsFromMap,
            ),
        url(r'inventory_review/parcel/(?P<parcel>[0-9]{7})/update$',
            staff_member_required(UniParcelUpdateView.as_view()),
            name='inventory_review_parcel_update'),
        url(r'inventory_review/map/$',
            staff_member_required(UniMapTemplateView.as_view()),
            name='inventory_review_map'),
        url(r'inventory_review/parcel/download\.csv$',
            get_uniinventory_csv,
            name='inventory_review_csv',
            ),
        url(r'condition_report/$',
            submitConditionReport,
            name='submit_condition_report'),

        url(r'condition_report_admin/(?P<parcel>[0-9]+)$',
            view_or_create_condition_report,
            name="find_or_create_and_redirect_cr_admin"),

        url(r'closing/deposit_slip/(?P<pk>[0-9]+)/$',
            staff_member_required(ClosingDepositSlipDetailView.as_view()),
            name='closing_deposit_slip'),

    #    url(r'epp/inventory.xlsx$', fetch_epp_inventory, name='epp_inventory_xlsx'),
        url(r'epp/inventory.xlsx$', PropertyInventoryList.as_view(), name='bf_inventory_xlsx'),


        url(r'nn/update/$', update_registered_organizations, name='update_registered_organizations'),
        url(r'donate/$', DonateView.as_view(), name='donate'),
        url(r'file/(?P<app_name>.*)/(?P<class_name>.*)/(?P<pk>[0-9]+)/(?P<field_name>.*)/$', send_class_file, name='send_class_file'),

        # commind - Commercial Industrial URLS
        url(r'^media/documents/(?P<filename>.*)', view_document, name='view_commind_document'),
        url(r'^commercial_industrial/application/$', CommIndApplicationFormView.as_view(), name='commind_application'),
        url(r'^commercial_industrial/app/detail/(?P<pk>[0-9]+)/', staff_member_required(CommIndApplicationDetailView.as_view()), name='commind_application_detail'),
        url(r'^commercial_industrial/application/(?P<parcel>[0-9]+)/', CommIndApplicationFormView.as_view(), name='commind_application_parcel'),
        url(r'^commercial_industrial/success/$', CommIndApplicationSuccessView.as_view(), name='commind_application_success'),
        url(r'^commercial_industrial/list/$', PropertyListView.as_view())


    ]

if settings.DEBUG:
    import debug_toolbar
    # static files (images, css, javascript, etc.)
    urlpatterns += [
                        url(r'^media/(?P<path>.*)$', serve, {
                            'document_root': settings.MEDIA_ROOT}),
                        url(r'^__debug__/', include(debug_toolbar.urls)),
                    ]
#urlpatterns += [        ]
