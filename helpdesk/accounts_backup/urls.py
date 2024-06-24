from django.urls import path
from .views import logout_view, MicrosoftLoginView, ProfileView

app_name = 'accounts'

urlpatterns = [
    path('logout/', logout_view, name='logout'),
    path('microsoft-login/', MicrosoftLoginView.as_view(), name='microsoft_login'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
