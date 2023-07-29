import re

PROTOCOLS_AND_WWW = {r"^https?:\/\/", r"^www\."}


def get_ip_address(request):
    """
    Function to retrieve the IP address from a request.

    If the 'HTTP_X_FORWARDED_FOR' header is present in the request, it uses the first IP address in this header
    (which can be a list if there are multiple, chained proxies).
    If this header is not present, it falls back to the 'REMOTE_ADDR' header, which is the IP address from
    which the request was sent.

    Parameters:
    request (HttpRequest): An HttpRequest object

    Returns:
    str: The IP address as a string.
    If no request or invalid request is provided, returns None.
    """
    ip_address = None
    if request and hasattr(request, "META"):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(",")[0]
        else:
            ip_address = request.META.get("REMOTE_ADDR")
    return ip_address


def get_user_agent(request):
    """
    Function to retrieve the User Agent string from a request.

    Parameters:
    request (HttpRequest): An HttpRequest object

    Returns:
    str: The User Agent string. If no request or invalid request is provided, returns 'unknown'.
    """
    user_agent = "unknown"
    if request and hasattr(request, "META"):
        user_agent = request.META.get("HTTP_USER_AGENT", "unknown")
    return user_agent


def get_referer_domain(request) -> str:
    """
    Function to retrieve the domain of the referer from a request.

    The function retrieves the 'HTTP_REFERER' header from the request, which contains the URL of the page that linked
    to the current page.
    It then removes any 'http://', 'https://', and 'www.' prefixes and extract the domain part from this URL.

    Parameters:
    request (HttpRequest): An HttpRequest object

    Returns:
    str: The domain of the referer as a string.
    If the referer header is not present, returns an empty string.
    """
    referer_header = request.META.get("HTTP_REFERER", "")
    for pattern in PROTOCOLS_AND_WWW:
        referer_header = re.sub(pattern, "", referer_header)
    referer_domain = referer_header.split("/")[0]
    return referer_domain
