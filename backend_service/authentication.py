import ipaddress
import logging

from django.conf import settings
from rest_framework.authentication import BaseAuthentication

from backend_service.exceptions import NotAuthorizedError
from utils.request_helpers import get_ip_address

logger = logging.getLogger('default')


class IPAddressAuthentication(BaseAuthentication):

    def authenticate(self, request):
        ip_address = get_ip_address(request)
        logger.info("Request is coming from %s", ip_address)
        if (
            '*' in settings.WHITELISTED_IP_ADDRESSES or
            ip_address in settings.WHITELISTED_IP_ADDRESSES or
            self._match_cidr(ip_address)
        ):
            return None
        raise NotAuthorizedError

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
