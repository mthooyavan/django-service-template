import re


def get_ip_address(request):
    if not request or not hasattr(request, 'META'):
        return None

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    return ip_address


def get_user_agent(request):
    return request.META.get('HTTP_USER_AGENT', 'unknown') if request and hasattr(request, 'META') else 'unknown'


def get_referer_domain(request) -> str:
    referer_header = request.META.get('HTTP_REFERER', '')
    referer_domain = re.sub(r'^www\.', '', re.sub(r'^https?:\/\/', '', referer_header).split('/')[0])
    return referer_domain
