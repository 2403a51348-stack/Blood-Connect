from django import forms
from .models import BloodRequest


class BloodRequestForm(forms.ModelForm):
    patient_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name or patient reference ID'})
    )
    blood_group = forms.ChoiceField(
        choices=BloodRequest.BLOOD_GROUPS,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    units_required = forms.IntegerField(
        min_value=1,
        max_value=20,
        initial=1,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    hospital_name = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Hospital or medical center name'})
    )
    hospital_address = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Hospital address, ward, room, or landmark'})
    )
    city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Hyderabad'})
    )
    state = forms.CharField(
        max_length=100,
        required=True,
        initial='Telangana',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Telangana'})
    )
    contact_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Attendant / coordinator contact name'})
    )
    contact_phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 9876543210'})
    )
    urgency = forms.ChoiceField(
        choices=BloodRequest.URGENCY_LEVELS,
        initial='HIGH',
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    additional_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Any specific medical instructions, replacement donor details, or critical notes'})
    )

    class Meta:
        model = BloodRequest
        fields = [
            'patient_name',
            'blood_group',
            'units_required',
            'hospital_name',
            'hospital_address',
            'city',
            'state',
            'contact_name',
            'contact_phone',
            'urgency',
            'additional_notes'
        ]
