from django.db import models
from property_inventory.models import Property

# put uploaded files in subdirectory based on address


def content_file_name(instance, filename):
    if instance.Property is None:
        return '/'.join(['annual_reports', 'no_address', filename])
    else:
        return '/'.join(['annual_reports', instance.Property.streetAddress, filename])


class annual_report(models.Model):

    parcel = models.CharField(max_length=7, blank=True, null=True)
    Property = models.ForeignKey(Property, blank=False, null=True)

    name = models.CharField(max_length=254, blank=False, null=False)
    organization = models.CharField(max_length=254, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=False, null=False)
    phone = models.CharField(max_length=12, blank=False, null=False)

    created = models.DateTimeField(auto_now_add=True)

    percent_completed = models.PositiveIntegerField(
        help_text="Roughly speaking, what percentage complete is this project?")

    past_expenses = models.PositiveIntegerField(
        help_text="It is ok to use rough estimates.", verbose_name='Funds spent to date')
    work_completed = models.TextField(max_length=5120, help_text="What work has been completed?",
                                      verbose_name='Written narative of the improvements made to date')

    work_remaining = models.TextField(
        max_length=5120, help_text="What work remains to be completed?", verbose_name='Work remaining')
    future_expenses = models.PositiveIntegerField(
        help_text="It is ok to use rough estimates.", verbose_name='Anticipated remaining expenses')

    feedback = models.TextField(
        max_length=5120, help_text="Do you have any other comments on your project or feedback for Renew Indianapolis about your experience with our program?", verbose_name='Feedback')

    STATE_CHOICES = (
        (True, u'Yes'),
        (False, u'No'),
    )

    certificate_of_completion_ready = models.BooleanField(
        verbose_name='Are you ready for a certificate of completion inspection?', help_text="If you select Yes then someone from the city will contact you to schedule the inspection.", choices=STATE_CHOICES, default=False)
    property_occupied = models.BooleanField(
        verbose_name='Is the property occupied?', choices=STATE_CHOICES, default=False)

    front_exterior_picture = models.ImageField(
        upload_to=content_file_name, blank=False)
    back_exterior_picture = models.ImageField(
        upload_to=content_file_name, blank=False)
    kitchen_picture = models.ImageField(
        upload_to=content_file_name, blank=False)
    bathroom_picture = models.ImageField(
        upload_to=content_file_name, blank=False)
    other_picture = models.ImageField(
        upload_to=content_file_name, blank=True, help_text='Project photo of your choice (optional)')

#    def image_tag(self):
#        return mark_safe('<img src="/media/%s" width="150" height="150" />' % (self.image))

#      image_tag.short_description = 'Image'
