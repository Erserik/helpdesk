from django.shortcuts import redirect, HttpResponse
from django.contrib.auth import login, logout
from django.views import View
from django.conf import settings
from urllib.parse import urlencode
import requests
from microsoft.services import microsoft_get_access_token, microsoft_get_user_info, user_get_or_create
import logging
from .models import CustomUser

from django.contrib.auth import get_user_model
User = get_user_model()

logger = logging.getLogger(__name__)

def logout_view(request):
    logout(request)
    return redirect('accounts:microsoft_login')  # Redirect to the Microsoft login page

def microsoft_login_url():
    """Generate URL for logging in through Microsoft for redirecting the user."""
    base_url = "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize".format(tenant_id=settings.MICROSOFT_AUTH_TENANT_ID)
    params = {
        'client_id': settings.MICROSOFT_AUTH_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': settings.MICROSOFT_REDIRECT_URI,
        'scope': 'openid email profile User.Read',
        'response_mode': 'query'
    }
    return f"{base_url}?{urlencode(params)}"

class ProfileView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('accounts:microsoft_login')
        user = request.user
        profile_info = f"Name: {user.get_full_name()}\nEmail: {user.email}"
        return HttpResponse(profile_info, content_type="text/plain")

class MicrosoftLoginView(View):
    def get(self, request, *args, **kwargs):
        error = request.GET.get('error')
        if error:
            # Redirect to an error page or show an error message
            return HttpResponse("Login error: " + error, status=401)

        code = request.GET.get('code')
        if not code:
            # Redirect to Microsoft's login URL
            return redirect(microsoft_login_url())

        # Exchange the code for an access token
        token_data = {
            'client_id': settings.MICROSOFT_AUTH_CLIENT_ID,
            'scope': 'openid email profile',
            'code': code,
            'redirect_uri': settings.MICROSOFT_REDIRECT_URI,
            'grant_type': 'authorization_code',
            'client_secret': settings.MICROSOFT_AUTH_CLIENT_SECRET,
        }
        token_r = requests.post("https://login.microsoftonline.com/common/oauth2/v2.0/token", data=token_data)
        token_r_json = token_r.json()
        access_token = token_r_json.get('access_token')

        # Use access token to get user info
        user_info_r = requests.get("https://graph.microsoft.com/v1.0/me", headers={'Authorization': f'Bearer {access_token}'})
        user_info = user_info_r.json()

        email = user_info.get('mail')  # Ensure mail is the correct key
        if not email:
            # Log this event or handle cases where email is not available
            logger.error("No email provided by Microsoft for user.")
            return redirect('orders:order_history')
            #zdes' oshibka nado fixit

        profile_data = {
            'email': email,
            'name': user_info.get('displayName', ''),
            'username': user_info.get('userPrincipalName', email)  # Use email if userPrincipalName is not available
        }

        # Here you could update or create a user in your local database
        user, _ = user_get_or_create(**profile_data)
        login(request, user=user)

        return redirect('orders:order_history')
