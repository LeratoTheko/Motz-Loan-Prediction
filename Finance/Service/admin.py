from django.contrib import admin
from .models import LoanApplication

@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'gender', 'married', 'education', 'self_employed',
        'applicant_income', 'coapplicant_income', 'loan_amount',
        'loan_amount_term', 'credit_history', 'predicted_status',
        'prediction_score', 'property_area', 'created_at'
    )
    list_filter = ('gender', 'married', 'education', 'self_employed', 'property_area', 'credit_history', 'predicted_status')
    search_fields = ('user__username',)
    ordering = ('-created_at',)
