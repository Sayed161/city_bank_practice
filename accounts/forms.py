from typing import Any
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .constant import ACCOUNT_TYPE,GENDER
from .models import UserBankAccount,UserAddress
from django import forms


class UserRegistrationForm(UserCreationForm):
    birth_date = forms.DateTimeField(widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=GENDER)	
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)	
    street_address = forms.CharField(max_length=255)
    city = forms.CharField(max_length=155)
    postal = forms.IntegerField()
    country = forms.CharField(max_length=155)
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2','first_name', 'last_name', 'email','account_type', 'birth_date', 'gender', 'street_address', 'country', 'postal','city']
        
    def save(self,commit=True):
        Our_user = super().save(commit=False)
        if commit == True :
            Our_user.save()
            account_type = self.cleaned_data.get('account_type')
            gender = self.cleaned_data.get('gender')
            postal = self.cleaned_data.get('postal')
            country = self.cleaned_data.get('country')
            birth_date = self.cleaned_data.get('birth_date')
            city = self.cleaned_data.get('city')
            street_address = self.cleaned_data.get('street_address')

            UserAddress.objects.create(
                user = Our_user,
                city = city,
                postal = postal,
                country = country,
                street_address = street_address,
            )

            UserBankAccount.objects.create(
                user = Our_user,
                account_type = account_type,
                gender = gender,
                birth_date = birth_date,
                account_no = 20240+12000000+Our_user.id
            )
        return Our_user
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class':(
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                )
            })


class UserProfileUpdate(forms.ModelForm):
    birth_date = forms.DateTimeField(widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=GENDER)	
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)	
    street_address = forms.CharField(max_length=255)
    city = forms.CharField(max_length=155)
    postal = forms.IntegerField()
    country = forms.CharField(max_length=155)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class':(
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                )
            })


        if self.instance :
            try:
                user_account = self.instance.accounts
                user_address = self.instance.address
            except UserBankAccount.DoesNotExist:
                user_account = None
                user_address = None

            if user_account :
                self.fields['account_type'].initial = user_account.account_type
                self.fields['gender'].initial = user_account.gender
                self.fields['birth_date'].initial = user_account.birth_date
                self.fields['street_address'].initial = user_address.street_address
                self.fields['city'].initial = user_address.city
                self.fields['postal'].initial = user_address.postal
                self.fields['country'].initial = user_address.country

    def save(self,commit=True):
        user = super().save(commit=False)
        if commit == True :
            user.save()

            user_account,created = UserBankAccount.objects.get_or_create(user=user)
            user_address,created = UserAddress.objects.get_or_create(user=user)

            user_account.account_type = self.cleaned_data['account_type']
            user_account.gender = self.cleaned_data['gender']
            user_account.birth_date = self.cleaned_data['birth_date']
            user_account.save()


            user_address.postal = self.cleaned_data['postal']
            user_address.country = self.cleaned_data['country']
            user_address.city = self.cleaned_data['city']
            user_address.street_address = self.cleaned_data['street_address']
            user_address.save()

        return user

            
    