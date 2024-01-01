from datetime import datetime
from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import CreateView,ListView,View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Transactions
from .forms import DepositForm,WithdrawForm,LoanRequestForm,SentForm
from .constants import DEPOSITE,WITHDRAW,LOAN,LOAN_PAID,SENT_MONEY
from django.contrib import messages
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models import Sum
from django.urls import reverse_lazy
from accounts.models import UserBankAccount
# Create your views here.


def send_transaction_email(user, amount, subject, template):
        message = render_to_string(template, {
            'user' : user,
            'amount' : amount,
        })
        send_email = EmailMultiAlternatives(subject, '', to=[user.email])
        send_email.attach_alternative(message, "text/html")
        send_email.send()

def send_email(user,reciver, amount, subject, template):
        message = render_to_string(template, {
            'user' : user,
            'amount' : amount,
            'reciver':reciver,
        })
        send_email = EmailMultiAlternatives(subject, '', to=[user.email,reciver])
        send_email.attach_alternative(message, "text/html")
        send_email.send()





class TransactionalMixin(LoginRequiredMixin, CreateView):
    template_name = 'transaction.html'
    model = Transactions
    title = ''
    success_url = reverse_lazy('transaction')

    def get_form_kwargs(self) :
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user,
        })
        return kwargs
    
    def get_context_data(self, **kwargs) :
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title,
        })
        return context

class DepositeMoneyView(TransactionalMixin):
    form_class = DepositForm
    title = "Deposite"

    def get_initial(self):
        initial = {'transactions_type':DEPOSITE}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.accounts
        account.balance += amount
        account.save(
            update_fields = ['balance']
        )
        messages.success(self.request,f"{amount}$ was deposited to your account successfully")
        
        send_transaction_email(self.request.user, amount, "Deposite Message", "deposite_mail.html")
        return super().form_valid(form)
    


class WithdrawMoneyView(TransactionalMixin):
    form_class = WithdrawForm
    title = "Withdraw Money"

    def get_initial(self):
        initial = {'transactions_type':WITHDRAW}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.accounts
        if not account.bank_rupt :
            account.balance -= amount
            account.save(
                update_fields = ['balance']
            )
            messages.success(self.request,f"{amount}$ was withdrawn from your account successfully")
            send_transaction_email(self.request.user, amount, "Withdraw Message", "withdraw_mail.html")
        else:
            messages.error(self.request,f"Bank has rupted you can't withdraw money")
        return super().form_valid(form)
    

class loanMoneyView(TransactionalMixin):
    form_class = LoanRequestForm
    title = "Request For Loan"

    def get_initial(self):
        initial = {'transactions_type':LOAN}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        current_loan_count = Transactions.objects.filter(account=self.request.user.accounts,transactions_type=LOAN,loan_approve= True).count()
        if current_loan_count >= 3:
            return HttpResponse("You have reached the limits")
        messages.success(self.request,f"Loan request for {amount}$ has been successfully sent to admin")
        send_transaction_email(self.request.user, amount, "Loan Request", "loan_mail.html")
        return super().form_valid(form)
    

class TransectionReportView(LoginRequiredMixin,ListView):
    template_name = "transaction_report.html"
    model = Transactions
    balance = 0

    def get_queryset(self):
        query_set = super().get_queryset().filter(account=self.request.user.accounts)
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')

        if start_date_str and end_date_str :
            start_date = datetime.strptime(start_date_str,"%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str,"%Y-%m-%d").date()
            query_set = query_set.filter(timestamp__date__gte = start_date,timestamp__date__lte = end_date )

            self.balance = Transactions.objects.filter(timestamp__date__gte = start_date,timestamp__date__lte = end_date ).aggregate(Sum('amount'))['amount__sum']
        else:
            self.balance = self.request.user.accounts.balance
        
        return query_set.distinct()
    
    def get_context_data(self, **kwargs) :
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.accounts,
        })
        return context
    
class PayloanView(LoginRequiredMixin,View):
    def get(self, request, loan_id):
        loan = get_object_or_404(Transactions,id = loan_id)

        if loan.loan_approve :
            user_account = loan.account

            if loan.amount < user_account.balance :
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.transactions_type = LOAN_PAID
                loan.save()
                send_transaction_email(self.request.user, loan.amount, "Loan Paid", "loan_paid_mail.html")
                return redirect ("loanlist")
            else:
                messages.error(self.request,f"You don't have enough money to pay the loan")
                return redirect("loanlist")
            
class LoanlistView(LoginRequiredMixin,ListView):
    model = Transactions
    template_name = "loan_request.html"
    context_object_name = "loans"
    title = "Loans"
    def get_queryset(self):
        user_account = self.request.user.accounts
        queryset = Transactions.objects.filter(account = user_account, transactions_type = LOAN)
        return queryset
    

class SentMoneyView(TransactionalMixin):
    form_class = SentForm
    title = "Sent Money"

    def get_initial(self):
        initial = {'transactions_type':SENT_MONEY}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        user_account = self.request.user.accounts
        reciver_ac = self.request.POST.get('reciver')

        try:
            reciver_account = UserBankAccount.objects.get(account_no=reciver_ac)
        except UserBankAccount.DoesNotExist:
            return HttpResponse("Reciver account not found")
        
        if user_account.balance >= amount:
                user_account.balance -= amount
                user_account.save(
                update_fields = ['balance']
                )

                reciver_account.balance += amount
                reciver_account.save(
                update_fields = ['balance']
                )
                send_email(self.request.user,reciver_account.user.email, amount, "Sent money", "sent_mail.html")
                messages.success(self.request,f"{amount} was sent to {reciver_ac} successfully")
            
        else:
                messages.error(self.request,"you don't have sufficient balance to send")
        return super().form_valid(form)