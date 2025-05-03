from django import forms
from .models import LoanApplication

class LoanApplicationForm(forms.ModelForm):
    class Meta:
        model = LoanApplication
        exclude = ['user', 'created_at']
        widgets = {
            field: forms.Select(attrs={'class': 'form-select'})
            for field in [
                'gender', 'married', 'dependents', 'education', 'self_employed',
                'property_area', 'credit_history'
            ]
        } | {
            field: forms.NumberInput(attrs={'class': 'form-control'})
            for field in ['applicant_income', 'coapplicant_income', 'loan_amount', 'loan_amount_term']
        }
