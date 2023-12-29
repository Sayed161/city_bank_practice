from django.urls import path,include
from .views import DepositeMoneyView,WithdrawMoneyView,LoanlistView,TransectionReportView,PayloanView,loanMoneyView
urlpatterns = [
    path('Deposite/', DepositeMoneyView.as_view(),name='deposite'),
    path('Withdrawl', WithdrawMoneyView.as_view(),name='withdrawl'),
    path('transaction/', TransectionReportView.as_view(),name='transaction'),
    path('pay_loan/<int:loan_id>/', PayloanView.as_view(),name='loan_pay'),
    path('loan_request/', loanMoneyView.as_view(),name='loan_request'),
    path('loanlist/', LoanlistView.as_view(),name='loanlist'),
]