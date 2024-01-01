from typing import Any
from django.contrib import admin
from .views import send_transaction_email
from . models import Transactions
# Register your models here.
@admin.register(Transactions)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['account','amount',"balance_after_transaction","transactions_type","loan_approve","bank_rupt"]
    def save_model(self, request, obj, form, change):
        if obj.loan_approve:
            obj.account.balance += obj.amount
            obj.balance_after_transaction = obj.account.balance
            obj.account.save()
            send_transaction_email(obj.account.user, obj.amount, "Loan Approval", "admin_mail.html")
            super().save_model(request, obj, form, change)