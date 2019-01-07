from django import forms
from .models import Patient, Array

class AddPatientForm(forms.ModelForm):
    check_array = forms.BooleanField(initial=True, required=False)

    class Meta:
        model = Patient
        fields = ['pid', 'name', 'dob', 'notes']
        widgets = {'dob': forms.SelectDateWidget(years=list(range(1930,2019)))}
        labels = {}
