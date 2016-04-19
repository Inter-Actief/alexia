from django import forms

from apps.billing.models import PermanentProduct, PriceGroup, ProductGroup, SellingPrice


class PermanentProductForm(forms.ModelForm):
    class Meta:
        model = PermanentProduct
        fields = ['name', 'productgroup', 'position', 'text_color', 'background_color']

    def __init__(self, organization, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.fields['productgroup'].queryset = ProductGroup.objects.filter(organization=organization)


class SellingPriceForm(forms.ModelForm):
    class Meta:
        model = SellingPrice
        fields = ['pricegroup', 'productgroup', 'price']

    def __init__(self, organization, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.fields['pricegroup'].queryset = PriceGroup.objects.filter(organization=organization)
        self.fields['productgroup'].queryset = ProductGroup.objects.filter(organization=organization)
