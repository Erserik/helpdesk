import requests
from typing import Dict, Any, Tuple
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth import get_user_model

User = get_user_model()


def error_auth_handling(response):
    response_json = response.json()
    if not response.ok:
        raise ValidationError(
            {
                'error': response_json.get('error'),
                'error_description': response_json.get('error_description')
            }
        )

def microsoft_validate_id_token(*, id_token: str) -> bool:
    response = requests.get(
        settings.OIDC_OP_JWKS_ENDPOINT,
        params={'id_token': id_token}
    )
    error_auth_handling(response)
    audience = response.json().get('aud')
    if audience != settings.OIDC_RP_CLIENT_ID:
        raise ValidationError('Invalid audience.')
    return True

def microsoft_get_access_token(*, code: str, redirect_uri: str) -> str:
    data = {
        'code': code,
        'client_id': settings.OIDC_RP_CLIENT_ID,
        'client_secret': settings.OIDC_RP_CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    response = requests.post(settings.OIDC_OP_TOKEN_ENDPOINT, data=data)
    error_auth_handling(response)
    return response.json().get('access_token')

def microsoft_get_user_info(*, access_token: str) -> Dict[str, Any]:
    response = requests.get(
        settings.OIDC_OP_USER_ENDPOINT,
        headers={'Authorization': f'Bearer {access_token}'}
    )
    error_auth_handling(response)
    return response.json()

def user_create(email, password=None, **extra_fields) -> User:
    # Check if email is not None, otherwise set a default or handle the case appropriately
    if email is None:
        raise ValueError("Email cannot be None")

    name = extra_fields.pop('name', None)
    if name:
        first_name, last_name = (name.split(' ', 1) + [''])[:2]
    else:
        first_name, last_name = '', ''

    # Ensure username is not passed twice by removing it from extra_fields
    extra_fields.pop('username', None)

    # Setting username to email, ensuring it's not None
    user = User(email=email, username=email, first_name=first_name, last_name=last_name, **extra_fields)
    if password:
        user.set_password(password)
    else:
        user.set_unusable_password()
    user.full_clean()
    user.save()
    return user

@transaction.atomic
def user_get_or_create(email, name, username):
    user, created = User.objects.get_or_create(
        username=username,  # Assumes username is unique
        defaults={'email': email, 'first_name': name.split()[0], 'last_name': name.split()[-1]}
    )
    if not created:
        # Update user details if already exists
        user.email = email
        user.first_name = name.split()[0]
        user.last_name = name.split()[-1]
        user.save()
    return user, created
