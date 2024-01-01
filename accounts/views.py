from django.shortcuts import render,redirect
from django.views.generic import FormView
from . forms import UserRegistrationForm,UserProfileUpdate
from django.contrib.auth import authenticate, login , update_session_auth_hash, logout
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth.views import LoginView,LogoutView
from django.views import View
from django.contrib.auth.forms import  PasswordChangeForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
# Create your views here. 

class userRegistrationview(FormView):
    template_name = "accounts/user_registration.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy('profile')
 
    def form_valid(self, form):
        user = form.save()
        login(self.request,user)
        print(user)
        return super().form_valid(form)
    
class UserLoginView(LoginView):
    template_name="accounts/user_login.html"
    def get_success_url(self) -> str:
        return reverse_lazy('home')
    

class Logout(LogoutView):
    def get_success_url(self) -> str:
        if self.request.user.is_authenticated:
            logout(self.request)
        return reverse_lazy('home')
    

def send_transaction_email(user, subject, template):
        message = render_to_string(template, {
            'user' : user,

        })
        send_email = EmailMultiAlternatives(subject, '', to=[user.email])
        send_email.attach_alternative(message, "text/html")
        send_email.send()
    

class profile(View):
    template_name = 'accounts/profile.html'

    def get(self, request):
        form = UserProfileUpdate(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserProfileUpdate(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the user's profile page
        return render(request, self.template_name, {'form': form})
    
def pass_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password Updated Successfully')
            update_session_auth_hash(request, form.user)
            send_transaction_email(request.user, "Password Changed", "accounts/pass_change_mail.html")
            return redirect('profile')
    
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'accounts/pass_change.html', {'form' : form})