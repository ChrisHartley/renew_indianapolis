from django import forms
from property_inventory.models import Property
from surplus.models import Parcel as SurplusProperty
from ncst.models import Property as NCSTProperty
from .models import photo

class DumpPhotosForm(forms.Form):
    #prop = forms.ModelChoiceField(queryset=Property.objects.filter(status__exact='Available').filter(structureType__contains='Residential Dwelling').order_by('streetAddress'))
    prop = forms.ModelChoiceField(queryset=Property.objects.all(), required=False)
    prop_surplus = forms.ModelChoiceField(queryset=SurplusProperty.objects.all(), required=False)
    prop_ncst = forms.ModelChoiceField(queryset=NCSTProperty.objects.all(), required=False)
    image1 = forms.ImageField(label="image 1", required=False)
    image2 = forms.ImageField(label="image 2", required=False)
    image3 = forms.ImageField(label="image 3", required=False)
    image4 = forms.ImageField(label="image 4", required=False)
    image5 = forms.ImageField(label="image 5", required=False)
    image6 = forms.ImageField(label="image 6", required=False)
    image7 = forms.ImageField(label="image 7", required=False)
    image8 = forms.ImageField(label="image 8", required=False)
    image9 = forms.ImageField(label="image 9", required=False)
    image10 = forms.ImageField(label="image 10", required=False)




    IMAGE_CHOICES = (
        ('0','None'),
        ('1','1'),
        ('2','2'),
        ('3','3'),
        ('4','4'),
        ('5','5'),
        ('6','6'),
        ('7','7'),
        ('8','8'),
        ('9','9'),
        ('10','10'),
    )
    primary_image = forms.ChoiceField(choices=IMAGE_CHOICES)

    def clean(self):
        cleaned_data = super(DumpPhotosForm, self).clean()
        prop = cleaned_data.get('prop')
        prop_surplus = cleaned_data.get('prop_surplus')
        prop_ncst = cleaned_data.get('prop_ncst')
        if prop is None and prop_surplus is None and prop_ncst is None:
            msg = "Must specify one property"
            self.add_error('prop', msg)
            self.add_error('prop_surplus', msg)
            self.add_error('prop_ncst', msg)


    def save_photos(self):
        for image, number in ( (self.cleaned_data.get('image1'), 1), (self.cleaned_data.get('image2'), 2), (self.cleaned_data.get('image3'), 3), (self.cleaned_data.get('image4'), 4), (self.cleaned_data.get('image5'), 5), (self.cleaned_data.get('image6'), 6), (self.cleaned_data.get('image7'), 7), (self.cleaned_data.get('image8'), 8), (self.cleaned_data.get('image9'), 9), (self.cleaned_data.get('image10'), 10) ):
            if number == int(self.cleaned_data.get('primary_image')):
                prime = True
            else:
                prime = False
            if image is not None:
                prop = self.cleaned_data.get('prop')
                prop_surplus = self.cleaned_data.get('prop_surplus')
                prop_ncst = self.cleaned_data.get('prop_ncst')
                if prop is not None:
                    p = photo(image=image, prop=prop, main_photo=prime)
                if prop_surplus is not None:
                    p = photo(image=image, prop_surplus=prop_surplus, main_photo=prime)
                if prop_ncst is not None:
                    p = photo(image=image, prop_ncst=prop_ncst, main_photo=prime)
                p.save()
