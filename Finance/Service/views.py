from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import  redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Avg, Q
from django.utils.timezone import now
from django.contrib.auth.models import Group

from .forms import LoanApplicationForm

from .models import LoanApplication

from .predictor import predict_loan_approval
from .predictor import predict_loan_amount


def base(request):
    return render(request, 'service/customer/base.html', {})



def welcome(request):
    return render(request, 'service/customer/welcome.html')



def signup_view(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password1
            )

            # Add user to 'Customer' group
            customer_group, created = Group.objects.get_or_create(name='Customer')
            user.groups.add(customer_group)

            messages.success(request, "Account created successfully. Please log in.")
            return redirect('login')  # Redirect to login page

    return render(request, 'service/auth/signup.html')





def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.groups.filter(name='Customer').exists():
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "You do not have permission to log in as a Customer.")
        else:
            messages.error(request, "Invalid credentials.")
            
    return render(request, 'service/auth/login.html')




def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_staff and user.groups.filter(name='Admin').exists():
                login(request, user)
                return redirect('admin_dashboard')  # Adjust to your admin dashboard URL name
            else:
                messages.error(request, "You do not have admin access.")
        else:
            messages.error(request, "Invalid credentials.")
            
    return render(request, 'service/auth/admin_login.html')



def logout_view(request):
    logout(request)
    return redirect('home')




@login_required(login_url='login')
def dashboard_view(request):
    user_loans = LoanApplication.objects.filter(user=request.user)
    total_loans = user_loans.count()
    approved_loans = user_loans.filter(predicted_status='Approved').count()
    
    unapproved_loans = user_loans.filter(
        Q(predicted_status__in=['Not Approved', 'Rejected by Customer']) |
        Q(predicted_status__isnull=True) |
        Q(predicted_status='')
    ).count()

    outstanding_balance = user_loans.filter(predicted_status='Approved').aggregate(
        total=Sum('loan_amount')
    )['total'] or 0

    chart_data = {
        'labels': ['Approved', 'Not Approved'],
        'values': [approved_loans, unapproved_loans],
    }

    context = {
        'total_loans': total_loans,
        'approved_loans': approved_loans,
        'unapproved_loans': unapproved_loans,
        'outstanding_balance': outstanding_balance,
        'chart_data': json.dumps(chart_data, cls=DjangoJSONEncoder)
    }
    return render(request, 'service/customer/dashboard.html', context)


    
"""
@login_required
def loan_application_view(request):
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user

            # Preprocess data
            gender = {'Male': 0, 'Female': 1}.get(application.gender, 0)
            married = {'No': 0, 'Yes': 1}.get(application.married, 0)
            education = {'Not Graduate': 0, 'Graduate': 1}.get(application.education, 0)
            self_employed = {'No': 0, 'Yes': 1}.get(application.self_employed, 0)
            dependents = {'0': 0, '1': 1, '2': 2, '3+': 3}.get(application.dependents, 0)
            property_area = {'Rural': 0, 'Semiurban': 1, 'Urban': 2}.get(application.property_area, 0)

            data = {
                'ApplicantIncome': application.applicant_income,
                'CoapplicantIncome': application.coapplicant_income,
                'LoanAmount': application.loan_amount,
                'Loan_Amount_Term': application.loan_amount_term,
                'Credit_History': application.credit_history,
                'Gender': gender,
                'Married': married,
                'Education': education,
                'Self_Employed': self_employed,
                'Dependents': dependents,
                'Property_Area': property_area,
                'TotalIncome': application.applicant_income + application.coapplicant_income,
                'IncomeToLoanTerm': (application.applicant_income + application.coapplicant_income) / max(application.loan_amount_term, 1),
            }

            # Perform prediction
            prediction, probability = predict_loan_approval(data)

            # Save application and prediction
            application.predicted_status = 'Approved' if prediction else 'Not Approved'
            application.prediction_score = probability
            application.save()

            return render(request, 'service/loan/loan_success.html', {
                'user': request.user,
                'application': application,
                'prediction': application.predicted_status,
                'probability': application.prediction_score,
            })
    else:
        form = LoanApplicationForm()

    return render(request, 'service/loan/apply_loan.html', {'form': form})


"""


@login_required
def loan_application_view(request):
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user

            # Preprocess categorical fields
            gender = {'Male': 0, 'Female': 1}.get(application.gender, 0)
            married = {'No': 0, 'Yes': 1}.get(application.married, 0)
            education = {'Not Graduate': 0, 'Graduate': 1}.get(application.education, 0)
            self_employed = {'No': 0, 'Yes': 1}.get(application.self_employed, 0)
            dependents = {'0': 0, '1': 1, '2': 2, '3+': 3}.get(application.dependents, 0)
            property_area = {'Rural': 0, 'Semiurban': 1, 'Urban': 2}.get(application.property_area, 0)

            total_income = application.applicant_income + application.coapplicant_income
            income_to_loan_term = total_income / max(application.loan_amount_term, 1)

            # Dictionary for both models
            data = {
                'ApplicantIncome': application.applicant_income,
                'CoapplicantIncome': application.coapplicant_income,
                'LoanAmount': application.loan_amount,
                'Loan_Amount_Term': application.loan_amount_term,
                'Credit_History': application.credit_history,
                'Gender': gender,
                'Married': married,
                'Education': education,
                'Self_Employed': self_employed,
                'Dependents': dependents,
                'Property_Area': property_area,
                'TotalIncome': total_income,
                'IncomeToLoanTerm': income_to_loan_term
            }

            # Predictions
            prediction, probability = predict_loan_approval(data)
            recommended_amount = predict_loan_amount(data)

            # Save results
            application.predicted_status = 'Approved' if prediction else 'Not Approved'
            application.prediction_score = probability
            if not prediction:
                application.recommended_amount = recommended_amount
            application.save()

            return render(request, 'service/loan/loan_success.html', {
                'user': request.user,
                'application': application,
                'prediction': application.predicted_status,
                'probability': application.prediction_score,
                'recommended_amount': recommended_amount if not prediction else None
            })

    else:
        form = LoanApplicationForm()

    return render(request, 'service/loan/apply_loan.html', {'form': form})




@login_required
def accept_recommended_loan(request, application_id):
    application = LoanApplication.objects.get(id=application_id, user=request.user)
    if application.predicted_status == 'Not Approved' and application.recommended_amount:
        application.loan_amount = application.recommended_amount
        application.predicted_status = 'Approved (Recommended)'
        application.save()
    return redirect('dashboard')





@login_required
def confirm_loan_amount_view(request, decision):
    app_id = request.session.get('application_id')
    data = request.session.get('loan_data')
    optimized_loan_amount = request.session.get('optimized_loan_amount')

    if not app_id or not data or optimized_loan_amount is None:
        return redirect('apply_loan')  # fallback

    application = LoanApplication.objects.get(id=app_id)

    if decision == 'accept':
        # Use optimized loan amount for prediction
        data['LoanAmount'] = optimized_loan_amount
        prediction, probability = predict_loan_approval(data)

        # Update the loan amount field in model
        application.loan_amount = optimized_loan_amount
        application.predicted_status = 'Approved' if prediction else 'Not Approved', '', 'Rejected by Customer'
        application.prediction_score = probability
        application.save()

        return render(request, 'service/loan/loan_success.html', {
            'user': request.user,
            'application': application,
            'prediction': application.predicted_status,
            'probability': application.prediction_score,
            'optimized_loan_amount': optimized_loan_amount,
        })
    else:
        application.predicted_status = 'Rejected by Customer'
        application.save()
        return render(request, 'service/loan/rejected_by_user.html', {'application': application})




@login_required
def loan_history_view(request):
    loan_history = LoanApplication.objects.filter(user=request.user).order_by('-created_at')

    load_status = LoanApplication.objects.filter(user=request.user)


    return render(request, 'service/loan/history.html', {'loan_history': loan_history})





def format_stats(queryset, label_key):
    return [
        {
            'label': item[label_key],
            'approved': item['approved'],
            'rejected': item['rejected']
        }
        for item in queryset
    ]




def admin_dashboard(request):
    today = now().date()
    today_loans = LoanApplication.objects.filter(created_at__date=today).count()
    total = LoanApplication.objects.count()
    approved = LoanApplication.objects.filter(predicted_status='Approved').count()
    denied = LoanApplication.objects.filter(predicted_status='Not Approved').count()
    avg_score = LoanApplication.objects.aggregate(avg=Avg('prediction_score'))['avg'] or 0

    gender_stats = LoanApplication.objects.values('gender').annotate(
        approved=Count('id', filter=Q(predicted_status='Approved')),
        rejected=Count('id', filter=Q(predicted_status='Not Approved'))
    )

    education = LoanApplication.objects.values('education').annotate(
        approved=Count('id', filter=Q(predicted_status='Approved')),
        rejected=Count('id', filter=Q(predicted_status='Not Approved'))
    )

    property_area = LoanApplication.objects.values('property_area').annotate(
        approved=Count('id', filter=Q(predicted_status='Approved')),
        rejected=Count('id', filter=Q(predicted_status='Not Approved'))
    )

    self_employed = LoanApplication.objects.values('self_employed').annotate(
        approved=Count('id', filter=Q(predicted_status='Approved')),
        rejected=Count('id', filter=Q(predicted_status='Not Approved'))
    )


    context = {
        'today_loans': today_loans,
        'approved': approved,
        'denied': denied,
        'total': total,
        'approval_rate': (approved / total * 100) if total else 0,
        'denial_rate': (denied / total * 100) if total else 0,
        'avg_score': round(avg_score, 2),
        'alert_drift': avg_score < 0.6 , # Threshold placeholder
        'gender_stats': list(gender_stats),
        'property_stats': format_stats(property_area, 'property_area'),
        'self_employed_stats': format_stats(self_employed, 'self_employed'),
        'education_stats': format_stats(education, 'education'),
    }
    return render(request, 'service/admin/admin_dashboard.html', context)



def admin_loan_history(request):
    loan_apps = LoanApplication.objects.all().order_by('-created_at')  # You can paginate if needed
    return render(request, 'service/admin/admin_loan_history.html', {'loan_apps': loan_apps})

