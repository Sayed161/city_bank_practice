from django.urls import path,include
from .views import userRegistrationview,UserLoginView,Logout,profile,pass_change
urlpatterns = [
    path('register/', userRegistrationview.as_view(),name='register'),
    path('login/', UserLoginView.as_view(),name='login'),
    path('logout/', Logout.as_view(),name='logout'),
    path('profile/', profile.as_view(),name='profile'),
    path('pass/', pass_change,name='pass'),
]
