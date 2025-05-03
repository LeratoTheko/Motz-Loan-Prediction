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



from .forms import LoanApplicationForm


from .models import LoanApplication

from .predictor import predict_loan_approval


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
            User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password1)
            messages.success(request, "Account created successfully. Please log in.")
            return redirect('login')  # Redirect to login page instead of logging in directly

    return render(request, 'service/auth/signup.html')




def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials.")
    return render(request, 'service/auth/login.html')



def logout_view(request):
    logout(request)
    return redirect('home')



@login_required(login_url='login')
def dashboard_view(request):
    user_loans = LoanApplication.objects.filter(user=request.user)
    total_loans = user_loans.count()
    approved_loans = user_loans.filter(predicted_status='Approved').count()
    unapproved_loans = user_loans.filter(predicted_status='Not Approved').count()

    # For now, treat all "Approved" loans as "Outstanding" unless you add a 'paid' field later
    outstanding_balance = user_loans.filter(predicted_status='Approved').aggregate(
        total=Sum('loan_amount')
    )['total'] or 0

    context = {
        'total_loans': total_loans,
        'approved_loans': approved_loans,
        'unapproved_loans': unapproved_loans,
        'outstanding_balance': outstanding_balance,
    }
    return render(request, 'service/customer/dashboard.html', context)





"""@login_required
def loan_application_view(request):
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.user = request.user
            loan.save()
            return redirect('application_success')
    else:
        form = LoanApplicationForm()
    
    return render(request, 'service/loan/apply_loan.html', {'form': form})"""



@login_required
def loan_application_view(request):
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user

            # Prepare data for prediction (ensure mapping is aligned with training)
            data = {
                'ApplicantIncome': application.applicant_income,
                'CoapplicantIncome': application.coapplicant_income,
                'LoanAmount': application.loan_amount,
                'Loan_Amount_Term': application.loan_amount_term,
                'Credit_History': application.credit_history,
                'Gender': {'Male': 0, 'Female': 1}.get(application.gender, 0),
                'Married': {'No': 0, 'Yes': 1}.get(application.married, 0),
                'Education': {'Not Graduate': 0, 'Graduate': 1}.get(application.education, 0),
                'Self_Employed': {'No': 0, 'Yes': 1}.get(application.self_employed, 0),
                'Dependents': {'0': 0, '1': 1, '2': 2, '3+': 3}.get(application.dependents, 0),
                'Property_Area': {'Rural': 0, 'Semiurban': 1, 'Urban': 2}.get(application.property_area, 0),
            }

            # Predict loan approval
            prediction, probability = predict_loan_approval(data)

            # Optionally store prediction in the model
            application.predicted_status = 'Approved' if prediction else 'Not Approved'
            application.prediction_score = probability  # Add this field in your model
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




@login_required
def loan_history_view(request):
    loan_history = LoanApplication.objects.filter(user=request.user).order_by('-created_at')

    load_status = LoanApplication.objects.filter(user=request.user)

    approved_loans = load_status.filter(predicted_status='Approved')
    unapproved_loans = load_status.filter(predicted_status='Not Approved')


    return render(request, 'service/loan/history.html', {'loan_history': loan_history})