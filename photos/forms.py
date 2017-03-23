from django import forms
from property_inventory.models import Property
from .models import photo

class DumpPhotosForm(forms.Form):
    #prop = forms.ModelChoiceField(queryset=Property.objects.filter(status__exact='Available').filter(structureType__contains='Residential Dwelling').order_by('streetAddress'))
    prop = forms.ModelChoiceField(queryset=Property.objects.all())
    image1 = forms.ImageField(label="image 1", required=False)
    image2 = forms.ImageField(label="image 2", required=False)
    image3 = forms.ImageField(label="image 3", required=False)
    image4 = forms.ImageField(label="image 4", required=False)
    image5 = forms.ImageField(label="image 5", required=False)

    IMAGE_CHOICES = (
        ('0','None'),
        ('1','1'),
        ('2','2'),
        ('3','3'),
        ('4','4'),
        ('5','5'),
    )
    primary_image = forms.ChoiceField(choices=IMAGE_CHOICES)

    def save_photos(self):
        for image, number in ( (self.cleaned_data.get('image1'), 1), (self.cleaned_data.get('image2'), 2), (self.cleaned_data.get('image3'), 3), (self.cleaned_data.get('image4'), 4), (self.cleaned_data.get('image5'), 5) ):
            print image, number
            if number == int(self.cleaned_data.get('primary_image')):
                prime = True
            else:
                prime = False
            if image is not None:
                p = photo(image=image, prop=self.cleaned_data.get('prop'), main_photo=prime)
                p.save()
