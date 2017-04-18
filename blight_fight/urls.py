from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic.base import TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required

from neighborhood_associations.views import get_relevant_neighborhood_assocations
from applications.views import ApplicationDetail, ApplicationDisplay, ApplicationNeighborhoodNotification, ApplicationPurchaseAgreement, ReviewCommitteeAgenda, ReviewCommitteeStaffSummary, CreateMeetingSupportArchive, ReviewCommitteeApplications
from photos.views import DumpPhotosView, PropertyPhotosView
from property_inventory.views import PropertyDetailView, BetaMapView
from applicants.views import edit_organization
from surplus.views import ParcelDetailView, ParcelDetailView, ParcelListView, SurplusMapTemplateView, ParcelUpdateView, surplusUpdateFieldsFromMap
# from applications.views import

admin.site.site_header = 'Blight Fight administration'

urlpatterns = patterns('',
        url(r'admin/', include(admin.site.urls)),
        url(r'^$', 'applicants.views.profile_home',
           name='applicants_home'),

        url(r'lookup_street_address/$', 'property_inventory.views.getAddressFromParcel',
           name='get_address_from_parcel'),

        url(r'admin-inquiry-list/$',
           'property_inquiry.views.inquiry_list'),

        url(r'property_inquiry/thanks/(?P<id>[0-9]+)$',
           'property_inquiry.views.property_inquiry_confirmation', name='property_inquiry_confirmation'),
        url(r'property_inquiry/$', 'property_inquiry.views.submitPropertyInquiry',
           name='submit_property_inquiry'),

        url(r'search-neighborhood-association/$',
           get_relevant_neighborhood_assocations.as_view()),
        url(r'search-neighborhood-association/(?P<parcel>[0-9]{7})/$',
           get_relevant_neighborhood_assocations.as_view()),

        url(r'application_status/$',
           'property_inventory.views.showApplications'),
        url(r'show/search/$', 'property_inventory.views.get_inventory_csv', name='inventory_download'),
        url(r'show/mdc_download/$', 'property_inventory.views.get_mdc_csv', name='mdc_download'),

        url(r'search_property/$',
           'property_inventory.views.searchProperties'),
        url(r'search-map/$',
           'property_inventory.views.searchProperties'),
#        url(r'map_beta/$',
#            BetaMapView.as_view()),

        url(r'surplus/$', SurplusMapTemplateView.as_view(), name='surplus_map'),
        url(r'surplus/search/$', 'surplus.views.searchSurplusProperties', name='surplus_search'),
        url(r'surplus/search2/$', 'surplus.views.searchSurplusProperties2', name='surplus_property_search2'),        
        url(r'surplus/property/(?P<parcel>[0-9]{7})/$', ParcelDetailView.as_view(), name='surplus_property'),
        url(r'surplus/property/update/$', 'surplus.views.surplusUpdateFieldsFromMap', name='surplus_property_update'),
        url(r'surplus/property/update/(?P<parcel>[0-9]{7})/$', ParcelUpdateView.as_view(), name='surplus_property_update_parcel'),



        url(r'propertyPopup/$',
           'property_inventory.views.propertyPopup'),
        url(r'property/(?P<parcel>[0-9]{7})/photos/$',
            PropertyPhotosView.as_view(), name='property_photos'),
        #                       url(r'property/(?P<parcel>[0-9]{7})/$',
        #                          PropertyDetailView.as_view(), name='property_detail'),


        url(r'admin-condition-report/$',
           'property_condition.views.condition_report_list'),
        url(r'condition_report/$',
           'property_condition.views.submitConditionReport'),

        url(r'annual-report/$',
           'annual_report_form.views.showAnnualReportForm'),
        url(r'view_annual_report/(?P<id>[0-9]+)/$',
           'annual_report_form.views.showAnnualReportData', name='view_annual_report'),
        url(r'admin_annual_report/$',
           'annual_report_form.views.showAnnualReportIndex'),
        url(r'admin_add_photos/$', staff_member_required(DumpPhotosView.as_view()), name="admin_add_photos"),

        url(r'accounts/profile$', 'applicants.views.profile_home',
           name='applicants_home'),
        url(r'accounts/profile/edit$',
           'applicants.views.showApplicantProfileForm', name='applicants_profile'),
        url(r'accounts/organization/new/$', login_required(edit_organization.as_view()),
           name='applicants_organization_add'),
        url(r'accounts/organization/edit/(?P<id>\w+)/$',
           login_required(edit_organization.as_view()), name='applicants_organization_edit'),
        url(r'accounts/organization$', 'applicants.views.show_organizations',
           name='applicants_organization'),

        # url(r'map/accounts/', include('allauth.urls')),
        # #django all-auth
        # django all-auth
        url(r'accounts/', include('allauth.urls')),

        url(r'utils/delete_file/$',
           'user_files.views.delete_uploaded_file', name='uploadedfile_delete'),
        url(r'utils/upload_file/$',
           'user_files.views.import_uploader', name='my_ajax_upload'),
        url(r'utils/download_file/(?P<id>\w+)$',
           'user_files.views.send_file', name='download_file'),

        url(r'application/thanks/(?P<id>[0-9]+)$',
           'applications.views.application_confirmation', name='application_confirmation'),

        url(r'application/view/(?P<pk>[0-9]+)/$', staff_member_required(ApplicationDetail.as_view()), name="application_summary_page"),
        url(r'application/view/complete/(?P<pk>[0-9]+)/$', staff_member_required(ApplicationDisplay.as_view()), name="application_detail_page"),
        url(r'application/view/neighborhood/(?P<pk>[0-9]+)/$',
            staff_member_required(ApplicationNeighborhoodNotification.as_view()),
            name='application_neighborhood_notification'),
        url(r'application/view/purchase_agreement/(?P<pk>[0-9]+)/$',
            staff_member_required(ApplicationPurchaseAgreement.as_view()),
            name='application_purchase_agreement'),
        url(r'meeting/view_agenda/(?P<pk>[0-9]+)/$',
             staff_member_required(ReviewCommitteeAgenda.as_view()),
             name='rc_agenda'),
        url(r'meeting/view_packet/(?P<pk>[0-9]+)/$',
            staff_member_required(ReviewCommitteeStaffSummary.as_view()),
            name='staff_packet'),
        url(r'meeting/view_packet/applications/(?P<pk>[0-9]+)/$',
            staff_member_required(ReviewCommitteeApplications.as_view()),
            name='application_packet'),

        url(r'meeting/view_packet_attachement/(?P<pk>[0-9]+)/$',
             staff_member_required(CreateMeetingSupportArchive.as_view()),
             name='staff_packet_attachements'),

        url(r'application/(?P<action>\w+)/$',
           'applications.views.process_application', name='process_application'),
        url(r'application/(?P<action>\w+)/(?P<id>[0-9]+)/$',
           'applications.views.process_application', name='process_application'),
    )

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
                            (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
                                'document_root': settings.MEDIA_ROOT}))
