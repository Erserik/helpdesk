import requests
from django import forms
from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.conf import settings
from urllib.parse import urlencode

from microsoft.services import microsoft_get_access_token, microsoft_get_user_info, user_get_or_create

def microsoft_login_url():
    """Constructs the Microsoft login URL to redirect the user."""
    base_url = f"https://login.microsoftonline.com/{settings.MICROSOFT_AUTH_TENANT_ID}/oauth2/v2.0/authorize"
    params = {
        'client_id': settings.MICROSOFT_AUTH_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': settings.MICROSOFT_REDIRECT_URI,
        'scope': 'openid email profile',
        'response_mode': 'query'
    }
    return f"{base_url}?{urlencode(params)}"

class MicrosoftLoginForm(forms.Form):
    code = forms.CharField(required=False)
    error = forms.CharField(required=False)


class MicrosoftLoginView(View):
    def get(self, request, *args, **kwargs):
        error = request.GET.get('error')
        if error:
            return HttpResponseRedirect(settings.BASE_FRONTEND_URL + '/login')

        code = request.GET.get('code')
        if not code:
            # Redirect to Microsoft's login URL
            return redirect(microsoft_login_url())

        # Exchange the code for an access token
        token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        token_data = {
            'client_id': settings.MICROSOFT_AUTH_CLIENT_ID,
            'scope': 'openid email profile',
            'code': code,
            'redirect_uri': settings.MICROSOFT_REDIRECT_URI,
            'grant_type': 'authorization_code',
            'client_secret': settings.MICROSOFT_AUTH_CLIENT_SECRET,
        }
        token_r = requests.post(token_url, data=token_data)
        token_r_json = token_r.json()
        access_token = token_r_json.get('access_token')

        # Use access token to get user info
        user_info_url = "https://graph.microsoft.com/v1.0/me"
        user_info_r = requests.get(user_info_url, headers={'Authorization': f'Bearer {access_token}'})
        user_info = user_info_r.json()

        profile_data = {
            'email': user_info.get('mail'),  # Ensure mail is the correct key
            'name': user_info.get('displayName'),  # This is the full name from Microsoft
            'username': user_info.get('userPrincipalName')  # Assuming the username is userPrincipalName
        }

        # Here you could update or create a user in your local database
        user, _ = user_get_or_create(**profile_data)
        login(request, user=user)

        return redirect('orders:user-profile')


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect("/")

#from django.shortcuts import render
#class UserProfileView(View):
 #   def get(self, request, *args, **kwargs):
  #      # Retrieve the full name directly from the logged-in user session
   #     email = request.user.email
    #    username = request.user.username
     #   return render(request, 'orders/submit_order.html', {
      #      'email': email,
       #     'username': username
        #})
