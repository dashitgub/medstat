from django import forms
from .models import UserDetails

class UserDetailsForm(forms.ModelForm):
    class Meta:
        model = UserDetails
        fields = ['gender', 'family_status', 'height', 'weight', 'lifestyle', 'sexual_activity', 'medication_allergy', 'medication_count', 'medication_frequency', 'smoking_frequency', 'alcohol_frequency']

        widgets = {
            'gender': forms.RadioSelect,
            'family_status': forms.Select,
            'lifestyle': forms.Select,
            'medication_frequency': forms.Select,
            'smoking_frequency': forms.Select,
            'alcohol_frequency': forms.Select,
        }
