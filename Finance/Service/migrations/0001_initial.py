# Generated by Django 5.2 on 2025-05-02 09:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LoanApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], max_length=10)),
                ('married', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], max_length=10)),
                ('dependents', models.CharField(choices=[('0', '0'), ('1', '1'), ('2', '2'), ('3+', '3+')], max_length=2)),
                ('education', models.CharField(choices=[('Graduate', 'Graduate'), ('Not Graduate', 'Not Graduate')], max_length=20)),
                ('self_employed', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], max_length=10)),
                ('applicant_income', models.PositiveIntegerField()),
                ('coapplicant_income', models.PositiveIntegerField()),
                ('loan_amount', models.PositiveIntegerField()),
                ('loan_amount_term', models.PositiveIntegerField(help_text='In months (e.g. 360)')),
                ('credit_history', models.IntegerField(choices=[(1, 'Yes'), (0, 'No')])),
                ('property_area', models.CharField(choices=[('Urban', 'Urban'), ('Semiurban', 'Semiurban'), ('Rural', 'Rural')], max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
