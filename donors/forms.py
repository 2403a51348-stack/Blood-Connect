from django import forms
from .models import DonationHistory


class DonationHistoryForm(forms.ModelForm):
    donation_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True
    )
    units_donated = forms.IntegerField(
        min_value=1,
        max_value=5,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    hospital_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Apollo Hospital, Jubilee Hills'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Additional remarks or recipient details'})
    )

    class Meta:
        model = DonationHistory
        fields = ['donation_date', 'units_donated', 'hospital_name', 'notes']
