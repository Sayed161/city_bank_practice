from django.shortcuts import render,redirect
from django.views.generic import FormView
from . forms import UserRegistrationForm,UserProfileUpdate
from django.contrib.auth import login,logout
from django.contrib.auth.views import LoginView,LogoutView
from django.views import View
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