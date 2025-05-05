from django.urls import path
from . import views

urlpatterns = [
    path('welcome-to-motz-financial-services', views.base, name="home"),
    path('', views.welcome, name="welcome"),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('customer/dashboard/', views.dashboard_view, name="dashboard"),
    path('customer/apply-loan/', views.loan_application_view, name='apply_loan'),
    # path('customer/loan-application-success', views.loan_application_success, name="application_success")

    path('customer/loan-history', views.loan_history_view, name="loan_history"),
    path('motz/admin/dashboard/loan-products-performance', views.admin_dashboard, name="admin_dashboard"),
    path('motz/admin/loan-history/', views.admin_loan_history, name='admin_loan_history'),
]