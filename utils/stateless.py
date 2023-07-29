import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from rest_framework_simplejwt.models import TokenUser

User = get_user_model()


class CustomAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if hasattr(settings, 'USERNAME') and username == settings.USERNAME:
            try:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    return user
                else:
                    return None
            except User.DoesNotExist:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    is_superuser=True,
                    is_staff=True,
                    is_active=True,
                )
            return user

        if (
            hasattr(settings, 'API_BASED_AUTHENTICATION') and
            hasattr(settings, 'AUTHENTICATION_APP_URL') and
            hasattr(settings, 'AUTHENTICATION_ENDPOINT') and
            settings.API_BASED_AUTHENTICATION
        ):
            response = requests.get(
                url=f'{settings.AUTHENTICATION_APP_URL}{settings.AUTHENTICATION_ENDPOINT}',
                timeout=5,
            )
            if response.status_code == 200:
                user_data = response.json()
                return self.get_user_by_data(user_data)
            else:
                return None

        # Use the default authentication method
        return super().authenticate(request, username, password, **kwargs)

    def get_user_by_data(self, user_data):
        try:
            user = User.objects.get(pk=user_data['id'])
            updated_keys = []
            for key, value in user_data.items():
                if hasattr(user, key):
                    updated_keys.append(key)
                    setattr(user, key, value)
            if updated_keys:
                user.save(update_fields=updated_keys)
        except User.DoesNotExist:
            user = User.objects.create(**user_data)

        return user


# pylint: disable=abstract-method
class CustomTokenUser(TokenUser):
    """
    A custom user model to be used with Simple JWT.
    TODO: Stateless authentication could be implemented in a better way,
     also has_perm and has_perms methods could be implemented. Similarly,
     other methods could be implemented as well.
    """
    @property
    def user_permissions(self):
        if (
            hasattr(settings, 'API_BASED_AUTHENTICATION') and
            hasattr(settings, 'AUTHENTICATION_APP_URL') and
            hasattr(settings, 'PERMISSIONS_ENDPOINT') and
            settings.API_BASED_AUTHENTICATION
        ):
            response = requests.get(
                url=f'{settings.AUTHENTICATION_APP_URL}{settings.PERMISSIONS_ENDPOINT}',
                timeout=5,
            )
            return response.json()
        if (
            hasattr(settings, 'CUSTOM_CLAIM') and
            hasattr(settings, 'PERMISSIONS_CLAIM')
        ):
            return self.token.get(settings.CUSTOM_CLAIM, {}).get(settings.PERMISSIONS_CLAIM, {})

        return super().user_permissions()
