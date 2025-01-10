from urllib.parse import urlparse
from apiflask.validators import Validator
from marshmallow import ValidationError
import re

# RegEx used for Validation
ip_regex = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
hostname_regex = re.compile(r'^(?!:\/\/)([a-zA-Z0-9.-]{1,253})\.([a-zA-Z]{2,63})$')

class URLValidator(Validator):
    def __init__(self, message=None):
        if message is None:
            message = "The string is not a valid URL."
        self.message = message

    def __call__(self, value):
        try:
            parsed = urlparse(value)
            # Check scheme and hostname
            if not parsed.scheme or not parsed.netloc:
                raise ValidationError(self.message)
            return
        except Exception:
            raise ValidationError(self.message)


class IPValidator(Validator):
    def __init__(self, message=None):
        if message is None:
            message = "The string is not a valid IP."
        self.message = message

    def __call__(self, value):
        if not validate_ip(value):
            raise ValidationError(self.message)
        return


class HostnameValidator(Validator):
    def __init__(self, message=None):
        if message is None:
            message = "The string is not a valid Hostname."
        self.message = message

    def __call__(self, value):
        if not validate_hostname(value):
            raise ValidationError(self.message)
        return


def validate_ip(ip_address):
    """
    Validate if the input is a valid IP address (IPv4).

    :param ip_address: The string to validate as an IP address.
    :return: True if the input is a valid IP address, otherwise False.
    """
    if not ip_regex.match(ip_address):
        return False

    # Ensure each segment (octet) is between 0-255
    return all(0 <= int(num) <= 255 for num in ip_address.split('.'))


def validate_hostname(hostname):
    """
    Validate if the input is a valid hostname (excluding protocol).

    :param hostname: The string to validate as a hostname.
    :return: True if the input is a valid hostname, otherwise False.
    """
    # Validate for valid 'localhost'
    if hostname == "localhost":
        return True

    if validate_ip(hostname):
        return True

    return bool(hostname_regex.match(hostname))
