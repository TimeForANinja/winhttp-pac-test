import ctypes
import struct
from ctypes import wintypes
from urllib.parse import urlparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from error_parser import parse_winhttp_error
import json
import re
import threading

# Constants for WinHTTP API
WINHTTP_ACCESS_TYPE_NO_PROXY = 1
WINHTTP_NO_PROXY_NAME = 0
WINHTTP_NO_PROXY_BYPASS = 0
WINHTTP_FLAG_ASYNC=0x10000000
WINHTTP_AUTOPROXY_CONFIG_URL = 0x00000002

WINHTTP_RESET_STATE = 0x00000001
WINHTTP_RESET_SWPAD_CURRENT_NETWORK = 0x00000002
WINHTTP_RESET_SWPAD_ALL = 0x00000004
WINHTTP_RESET_SCRIPT_CACHE = 0x00000008
WINHTTP_RESET_ALL = 0x0000FFFF
WINHTTP_RESET_NOTIFY_NETWORK_CHANGED = 0x00010000
WINHTTP_RESET_OUT_OF_PROC = 0x00020000

# Regex for Validations
ip_regex = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
hostname_regex = re.compile(r'^(?!:\/\/)([a-zA-Z0-9.-]{1,253})\.([a-zA-Z]{2,63})$')


class ProxyHandlerServer(BaseHTTPRequestHandler):
    def send_json_response(self, json_body, status_code):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(json_body).encode('utf-8'))

    def do_GET(self):
        if self.path == "/up":
            # Respond to /up route with JSON
            self.send_json_response({"status": 'success', "message": "Server is up and running!"}, 200)
        else:
            # Default response for GET
            self.send_json_response({"status": "failed", "error": "Not Found"}, 404)

    def do_POST(self):
        # Parse JSON payload
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data)
        except json.JSONDecodeError:
            self.send_json_response({'status': 'failed',"error": "Request must be a valid JSON"}, 400)
            return

        # Validate input
        pac_url = data.get("pac", {}).get("url")
        dest_host = data.get("dest_host")

        if not pac_url:
            self.send_json_response({'status': 'failed',"error": "Field 'pac.url' is required"}, 400)
            return

        if not dest_host:
            self.send_json_response({'status': 'failed',"error": "Field 'dest_host' is required"}, 400)
            return

        # Validate the format of URLs
        if not ProxyHandlerServer.validate_url(pac_url):
            self.send_json_response({'status': 'failed',"error": "'pac.url' must be a valid URL"}, 400)
            return

        if not ProxyHandlerServer.validate_hostname(dest_host):
            self.send_json_response({'status': 'failed',"error": "'dest_host' must be a valid Hostname"}, 400)
            return

        try:
            eval_result = resolve_proxy_with_pac(dest_host, pac_url)
            self.send_json_response(eval_result, 200)
        except Exception as e:
            self.send_json_response({'status': 'failed',"error": "Unexpected Error during evaluation", "message": str(e)}, 500)

    @staticmethod
    def validate_url(url):
        try:
            parsed = urlparse(url)
            # Check scheme and hostname
            if not parsed.scheme or not parsed.netloc:
                return False
            return True
        except Exception:
            return False

    @staticmethod
    def validate_ip(ip_address: str) -> bool:
        """
        Validate if the input is a valid IP address (IPv4).

        :param ip_address: The string to validate as an IP address.
        :return: True if the input is a valid IP address, otherwise False.
        """
        if not ip_regex.match(ip_address):
            return False

        # Ensure each segment (octet) is between 0-255
        return all(0 <= int(num) <= 255 for num in ip_address.split('.'))

    @staticmethod
    def validate_hostname(hostname: str) -> bool:
        """
        Validate if the input is a valid hostname (excluding protocol).

        :param hostname: The string to validate as a hostname.
        :return: True if the input is a valid hostname, otherwise False.
        """
        # Validate for valid 'localhost'
        if hostname == "localhost":
            return True

        if ProxyHandlerServer.validate_ip(hostname):
            return True

        return bool(hostname_regex.match(hostname))

    @staticmethod
    def new_server(port=8082):
        server_address = ('0.0.0.0', port)
        httpd = HTTPServer(server_address, ProxyHandlerServer)
        print(f"Starting server on port {port}...")
        httpd.serve_forever()


class WINHTTP_AUTOPROXY_OPTIONS(ctypes.Structure):
    _fields_ = [
        ("dwFlags", ctypes.wintypes.DWORD),
        ("dwAutoDetectFlags", ctypes.wintypes.DWORD),
        ("lpszAutoConfigUrl", ctypes.wintypes.LPCWSTR),
        ("lpvReserved", ctypes.c_void_p),
        ("dwReserved", ctypes.wintypes.DWORD),
        ("fAutoLogonIfChallenged", ctypes.wintypes.BOOL)
    ]


class WINHTTP_PROXY_INFO(ctypes.Structure):
    _fields_ = [
        ("dwAccessType", ctypes.wintypes.DWORD),
        ("lpszProxy", ctypes.wintypes.LPCWSTR),
        ("lpszProxyBypass", ctypes.wintypes.LPCWSTR)
    ]

winhttp = None
def init_winhttp():
    global winhttp
    winhttp = ctypes.windll.LoadLibrary("winhttp.dll")

    # check support
    print("Platform", "supported" if winhttp.WinHttpCheckPlatform() else "unsupported")
    if winhttp.WinHttpCheckPlatform() == 0:
        raise Exception("WinHTTP is not supported on this platform.")

def resolve_proxy_with_pac(dest_host, pac_url) -> dict:
    """Uses WinHTTP to resolve the proxy for the given URL using the PAC file."""
    with threading.Lock():
        # prep input params
        destination_url = f"https://{dest_host}/test"
        print("dest_host", dest_host, "destination_url", destination_url, "pac_url", pac_url)

        # Initialize WinHTTP session
        hSession = winhttp.WinHttpOpen(
            ctypes.c_wchar_p("WinHTTP-Engine"),  # user agent string
            WINHTTP_ACCESS_TYPE_NO_PROXY,
            WINHTTP_NO_PROXY_NAME,
            WINHTTP_NO_PROXY_BYPASS,
            WINHTTP_FLAG_ASYNC,
        )
        print("Session created", hSession)
        if not hSession:
            return parse_winhttp_error("WinHttpOpen", ctypes.GetLastError())

        # force clear cache
        #result = winhttp.WinHttpResetAutoProxy(
        #    hSession,
        #    WINHTTP_RESET_NOTIFY_NETWORK_CHANGED | WINHTTP_RESET_OUT_OF_PROC | WINHTTP_RESET_ALL,
        #)
        #print("Clearing Cache", "successfull" if result==0 else f"failed with code {result}")

        try:
            auto_proxy_options = WINHTTP_AUTOPROXY_OPTIONS()
            auto_proxy_options.dwFlags = WINHTTP_AUTOPROXY_CONFIG_URL
            auto_proxy_options.dwAutoDetectFlags = 0
            auto_proxy_options.lpszAutoConfigUrl = ctypes.wintypes.LPCWSTR(pac_url)
            auto_proxy_options.fAutoLogonIfChallenged = False

            proxy_info = WINHTTP_PROXY_INFO()

            # Call WinHttpGetProxyForUrl
            result = winhttp.WinHttpGetProxyForUrl(
                hSession,
                ctypes.wintypes.LPCWSTR(destination_url),
                ctypes.byref(auto_proxy_options),
                ctypes.byref(proxy_info),
            )

            if not result:
                return parse_winhttp_error("WinHttpGetProxyForUrl", ctypes.GetLastError())

            # Extract the proxy string from proxy_info
            proxy = proxy_info.lpszProxy if proxy_info.lpszProxy else "DIRECT"
            return {
                'status': 'success',
                'proxy': proxy,
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error_code': 1,
                'error': f"Failed to parse PAC: {str(e)}"
            }

        finally:
            # Properly close the WinHTTP session handle
            winhttp.WinHttpCloseHandle(hSession)


class InvalidArchitectureError(Exception):
    """Custom exception for invalid Python architecture."""
    pass

    @staticmethod
    def is_python_32bit():
        return struct.calcsize("P") * 8 == 32


if __name__ == "__main__":
    if not InvalidArchitectureError.is_python_32bit():
        raise InvalidArchitectureError("WinHTTP must be running on 32-bit architecture.")
    init_winhttp()

    ProxyHandlerServer.new_server()
