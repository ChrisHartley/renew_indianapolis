from django.db import models
from property_inventory.models import Property
from django.utils.encoding import python_2_unicode_compatible

# put uploaded files in subdirectory based on address


def content_file_name(instance, filename):
    if instance.Property is None:
        return '/'.join(['annual_reports', 'no_address', filename])
    else:
        return '/'.join(['annual_reports', instance.Property.streetAddress, filename])

@python_2_unicode_compatible
class annual_report(models.Model):

    parcel = models.CharField(max_length=7, blank=True, null=True)
    Property = models.ForeignKey(Property, blank=False, null=True)

    name = models.CharField(max_length=254, blank=False, null=False)
    organization = models.CharField(max_length=254, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=False, null=False)
    phone = models.CharField(max_length=12, blank=False, null=False)
    sold = models.NullBooleanField(blank=True, help_text='Have you have sold or transferred this property?', verbose_name='Re-sold?')
    resale_buyer = models.CharField(max_length=1024, blank=True, help_text='Name of person or entity who purchased the property from you.')

    created = models.DateTimeField(auto_now_add=True)

    percent_completed = models.PositiveIntegerField(
        help_text="Roughly speaking, what percentage complete is this project?", blank=True, null=True)

    past_expenses = models.PositiveIntegerField(
        help_text="It is ok to use rough estimates.", verbose_name='Funds spent to date', blank=True, null=True)
    work_completed = models.TextField(max_length=5120, help_text="What work has been completed?",
                                      verbose_name='Written narative of the improvements made to date',
                                      blank=True)

    work_remaining = models.TextField(
        max_length=5120, help_text="What work remains to be completed?",
        verbose_name='Work remaining',
        blank=True)
    future_expenses = models.PositiveIntegerField(
        help_text="It is ok to use rough estimates.",
        verbose_name='Anticipated remaining expenses',
        blank=True, null=True)

    feedback = models.TextField(
        max_length=5120, help_text="Do you have any other comments on your project or feedback for Renew Indianapolis about your experience with our program?",
        verbose_name='Feedback',
        blank=True)

    STATE_CHOICES = (
        (True, 'Yes'),
        (False, 'No'),
    )

    certificate_of_completion_ready = models.BooleanField(
        verbose_name='Are you ready for a certificate of completion inspection?', help_text="If you select Yes then someone from the city will contact you to schedule the inspection.", choices=STATE_CHOICES, default=False)
    property_occupied = models.BooleanField(
        verbose_name='Is the property occupied?', choices=STATE_CHOICES, default=False)

    lot_picture = models.ImageField(upload_to=content_file_name, blank=True, help_text='Photo of the lot')
    front_exterior_picture = models.ImageField(
        upload_to=content_file_name, blank=True)
    back_exterior_picture = models.ImageField(
        upload_to=content_file_name, blank=True)
    kitchen_picture = models.ImageField(
        upload_to=content_file_name, blank=True)
    bathroom_picture = models.ImageField(
        upload_to=content_file_name, blank=True)
    other_picture = models.ImageField(
        upload_to=content_file_name, blank=True, help_text='Project photo of your choice (optional)')

    def __str__(self):
        return '{0} - {1} - {2}'.format(self.Property, self.created, self.certificate_of_completion_ready)


#    def image_tag(self):
#        return mark_safe('<img src="/media/%s" width="150" height="150" />' % (self.image))

#      image_tag.short_description = 'Image'
