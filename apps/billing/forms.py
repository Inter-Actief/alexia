from django.forms.models import ModelForm

from apps.billing.models import PermanentProduct, PriceGroup, ProductGroup, SellingPrice


class PermanentProductForm(ModelForm):
    """
    Form for PermanentProduct objects.

    Limits ProductGroup selecting to specified organization.
    """

    def __init__(self, organization, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['productgroup'].queryset = ProductGroup.objects.filter(organization=organization)

    class Meta:
        model = PermanentProduct
        fields = ['name', 'productgroup', 'stockproduct', 'position', 'text_color', 'background_color']


class SellingPriceForm(ModelForm):
    """
    Form for PermanentProduct objects.

    Limits ProductGroup selecting to specified organization.
    """

    def __init__(self, organization, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['pricegroup'].queryset = PriceGroup.objects.filter(organization=organization)
        self.fields['productgroup'].queryset = ProductGroup.objects.filter(organization=organization)

    class Meta:
        model = SellingPrice
        fields = ['pricegroup', 'productgroup', 'price']
