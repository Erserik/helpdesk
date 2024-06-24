from django.urls import path
from .views import login_view, logout_view, MicrosoftLoginView, home_view

app_name = 'accounts'

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('microsoft-login/', MicrosoftLoginView.as_view(), name='microsoft_login'),
    path('home/', home_view, name='home'),
]
