from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.views import View
from django.conf import settings
from urllib.parse import urlencode
import requests
from microsoft.services import user_get_or_create

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('orders:order_history')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('accounts:login')

def microsoft_login_url():
    """Создание URL для входа через Microsoft для перенаправления пользователя."""
    base_url = f"https://login.microsoftonline.com/{settings.MICROSOFT_AUTH_TENANT_ID}/oauth2/v2.0/authorize"
    params = {
        'client_id': settings.MICROSOFT_AUTH_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': settings.MICROSOFT_REDIRECT_URI,
        'scope': 'openid email profile',
        'response_mode': 'query'
    }
    return f"{base_url}?{urlencode(params)}"

def home_view(request):
    return render(request, 'home.html')

class MicrosoftLoginView(View):
    def get(self, request, *args, **kwargs):
        error = request.GET.get('error')

        code = request.GET.get('code')
        if not code:
            # Перенаправление на URL для входа через Microsoft
            return redirect(microsoft_login_url())

        try:
            # Обмен кода на токен доступа
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
            token_r.raise_for_status()  # Поднять HTTPError для плохих ответов
            token_r_json = token_r.json()
            access_token = token_r_json.get('access_token')

            if not access_token:
                return HttpResponseRedirect(settings.BASE_FRONTEND_URL + '/login')

            # Использование токена доступа для получения информации о пользователе
            user_info_url = "https://graph.microsoft.com/v1.0/me"
            user_info_r = requests.get(user_info_url, headers={'Authorization': f'Bearer {access_token}'})
            user_info_r.raise_for_status()
            user_info = user_info_r.json()

            profile_data = {
                'email': user_info.get('mail'),
                'name': user_info.get('displayName'),
                'username': user_info.get('userPrincipalName') or user_info.get('mail')  # Ensure 'username' is included
            }

            if not profile_data['email']:
                # Обработка случаев, когда email недоступен
                return HttpResponseRedirect(settings.BASE_FRONTEND_URL + '/login')

            user, _ = user_get_or_create(**profile_data)
            login(request, user=user)
        except requests.RequestException as e:
            # Логирование исключений и редирект на страницу входа с сообщением об ошибке
            print(f"Ошибка запроса: {e}")
            return HttpResponseRedirect(settings.BASE_FRONTEND_URL + '/login')

        return redirect("orders:order_history")
