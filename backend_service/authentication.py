import ipaddress
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework_simplejwt.authentication import (
    JWTAuthentication as DefaultJWTAuthentication,
)
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import BlacklistMixin, Token

from backend_service.exceptions import (
    InvalidTokenAPIException,
    NotAuthorizedAPIException,
)
from backend_service.logging import thread_local_storage
from utils.request_helpers import get_ip_address
from utils.tokens import decoded_token

logger = logging.getLogger("default")

User = get_user_model()


class AccessToken(BlacklistMixin, Token):
    token_type = "access"  # nosec
    lifetime = api_settings.ACCESS_TOKEN_LIFETIME


class IPAddressAuthentication(BaseAuthentication):
    def authenticate(self, request):
        ip_address = get_ip_address(request)
        logger.info("Request is coming from %s", ip_address)
        if (
            "*" in settings.WHITELISTED_IP_ADDRESSES
            or ip_address in settings.WHITELISTED_IP_ADDRESSES
            or self._match_cidr(ip_address)
        ):
            return None
        raise NotAuthorizedAPIException

    @staticmethod
    def _match_cidr(ip_address):
        for cidr in settings.WHITELISTED_CIDR:
            # create an ipaddress.IPv4Address object from the IP address string
            ip_address = ipaddress.IPv4Address(ip_address)

            # create an ipaddress.IPv4Network object from the subnet string
            subnet = ipaddress.IPv4Network(cidr)

            # check if the IP address is within the subnet
            if ip_address in subnet:
                return True

        return False


class JWTAuthentication(DefaultJWTAuthentication):
    def get_validated_token(self, raw_token: bytes) -> Token:
        for token_class in api_settings.AUTH_TOKEN_CLASSES:
            try:
                validated_token = token_class(raw_token)
                validated_token = decoded_token(validated_token)
                return validated_token
            except TokenError as e:
                logger.debug(
                    {
                        "token_class": token_class.__name__,
                        "token_type": token_class.token_type,
                        "message": e.args[0],
                    }
                )

        raise InvalidTokenAPIException

    def get_user(self, validated_token):
        user_id = validated_token.get("user_id")
        if (
            "custom_claim" not in validated_token
            or "role" not in validated_token["custom_claim"]
        ):
            logger.error(
                "Suspicious Authentication Attempt: No custom_claim or role found in token"
            )
            user = None
        else:
            try:
                user = User.objects.get(uuid=user_id)
                user.role = type(
                    "Role", (object,), validated_token["custom_claim"]["role"]
                )
            except User.DoesNotExist:
                logger.error(
                    "Suspicious Authentication Attempt: No user found for user_id: %s",
                    user_id,
                )
                user = None
            else:
                thread_local_storage.user_id = user.uuid
                thread_local_storage.org_id = user.organisation_id

        return user
