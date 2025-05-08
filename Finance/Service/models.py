from django.db import models
from django.contrib.auth.models import User

class LoanApplication(models.Model):
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female')]
    MARRIED_CHOICES = [('Yes', 'Yes'), ('No', 'No')]
    DEPENDENTS_CHOICES = [('0', '0'), ('1', '1'), ('2', '2'), ('3+', '3+')]
    EDUCATION_CHOICES = [('Graduate', 'Graduate'), ('Not Graduate', 'Not Graduate')]
    SELF_EMPLOYED_CHOICES = [('Yes', 'Yes'), ('No', 'No')]
    PROPERTY_AREA_CHOICES = [('Urban', 'Urban'), ('Semiurban', 'Semiurban'), ('Rural', 'Rural')]
    CREDIT_HISTORY_CHOICES = [(1, 'Yes'), (0, 'No')]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    married = models.CharField(max_length=10, choices=MARRIED_CHOICES)
    dependents = models.CharField(max_length=2, choices=DEPENDENTS_CHOICES)
    education = models.CharField(max_length=20, choices=EDUCATION_CHOICES)
    self_employed = models.CharField(max_length=10, choices=SELF_EMPLOYED_CHOICES)

    applicant_income = models.PositiveIntegerField()
    coapplicant_income = models.PositiveIntegerField()

    loan_amount = models.PositiveIntegerField()
    loan_amount_term = models.PositiveIntegerField(help_text="In months (e.g. 360)")
    credit_history = models.IntegerField(choices=CREDIT_HISTORY_CHOICES)

    predicted_status = models.CharField(max_length=20, null=True, blank=True)
    prediction_score = models.FloatField(null=True, blank=True)


    property_area = models.CharField(max_length=20, choices=PROPERTY_AREA_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    recommended_amount = models.PositiveIntegerField(null=True, blank=True, help_text="Suggested amount if initial request not approved")


    def __str__(self):
        return f"Loan Application by {self.user.username}"
