from django.urls import path

from microsoft.views import MicrosoftLoginView, LogoutView

app_name = 'microsoft'

urlpatterns = [
    path('callback/', MicrosoftLoginView.as_view(), name='login-with-microsoft'),
    path('logout/', LogoutView.as_view(), name='logout'),
#path('profile/', UserProfileView.as_view(), name='user-profile'),
]
