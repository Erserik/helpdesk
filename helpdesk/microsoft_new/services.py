import requests
from typing import Dict, Any, Tuple

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth import get_user_model

User = get_user_model()  # This will get the custom user model

def error_auth_handling(response):
    response_json = response.json()

    if not response.ok:
        raise ValidationError(
            {
                'error': response_json['error'],
                'error_description': response_json['error_description']
            }
        )

def microsoft_validate_id_token(*, id_token: str) -> bool:
    response = requests.get(
        settings.OIDC_OP_JWKS_ENDPOINT,
        params={'id_token': id_token}
    )

    error_auth_handling(response)

    audience = response.json()['aud']

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

    access_token = response.json()['access_token']

    return access_token

def microsoft_get_user_info(*, access_token: str) -> Dict[str, Any]:
    response = requests.get(
        settings.OIDC_OP_USER_ENDPOINT,
        headers={'Authorization': f'Bearer {access_token}'}
    )

    error_auth_handling(response)

    return response.json()

def user_create(email, password=None, **extra_fields) -> User:
    extra_fields = {
        'is_staff': False,
        'is_superuser': False,
        **extra_fields
    }

    user = User(email=email, username=email, **extra_fields)

    if password:
        user.set_password(password)
    else:
        user.set_unusable_password()

    user.full_clean()
    user.save()

    return user

@transaction.atomic
def user_get_or_create(*, email: str, **extra_data) -> Tuple[User, bool]:
    user = User.objects.filter(email=email).first()

    if user:
        # Update the user with valid fields only
        valid_fields = {k: v for k, v in extra_data.items() if hasattr(user, k)}
        for field, value in valid_fields.items():
            setattr(user, field, value)
        user.save()
        return user, False

    # Pass only valid fields when creating a new user
    valid_fields = {k: v for k, v in extra_data.items() if hasattr(User, k)}
    return user_create(email=email, **valid_fields), True
