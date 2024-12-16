import argparse
import os
import threading
import time
import requests
from requests.exceptions import ConnectionError
from flask import Flask, send_from_directory, request
import ctypes
from ctypes import wintypes

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

# Flask app setup
app = Flask(__name__)
pac_file_path = ""


@app.route('/pac/<path:filename>', methods=['GET'])
def serve_pac(filename):
    print(f"Serving PAC file: {filename}")
    return send_from_directory(os.path.dirname(pac_file_path), filename)


@app.route('/up', methods=['GET'])
def serve_up():
    return "hello world"


def start_webserver():
    app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False)


def wait_for_server(url, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("Server is ready!")
                return True
        except ConnectionError:
            pass
        time.sleep(0.1)  # Small delay between retries
    raise TimeoutError(f"Server {url} did not start within {timeout} seconds")


class WINHTTP_AUTOPROXY_OPTIONS(ctypes.Structure):
    _fields_ = [
        ("dwFlags", ctypes.wintypes.DWORD),
        ("dwAutoDetectFlags", ctypes.wintypes.DWORD),
        ("lpszAutoConfigUrl", ctypes.wintypes.LPCWSTR),
        #("lpvReserved", ctypes.c_void_p),
        #("dwReserved", ctypes.wintypes.DWORD),
        ("fAutoLogonIfChallenged", ctypes.wintypes.BOOL)
    ]


class WINHTTP_PROXY_INFO(ctypes.Structure):
    _fields_ = [
        ("dwAccessType", ctypes.wintypes.DWORD),
        ("lpszProxy", ctypes.wintypes.LPCWSTR),
        ("lpszProxyBypass", ctypes.wintypes.LPCWSTR)
    ]


def showLastError(funcName, alignment=0):
    error_id = ctypes.GetLastError()
    print(' ' * alignment + '[-] Error on %s: %s' % (funcName, error_id))

    # https://learn.microsoft.com/en-us/windows/win32/winhttp/error-messages
    if error_id == 12167:
        title = 'ERROR_WINHTTP_UNABLE_TO_DOWNLOAD_SCRIPT'
        message = 'The PAC file cannot be downloaded. For example, the server referenced by the PAC URL may not have been reachable, or the server returned a 404 NOT FOUND response.'
    elif error_id == 12007:
        title = 'ERROR_WINHTTP_NAME_NOT_RESOLVED'
        message = 'The server name cannot be resolved.'
    elif error_id == 12029:
        title = 'ERROR_WINHTTP_CANNOT_CONNECT'
        message = 'Returned if connection to the server failed.'
    elif error_id == 12002:
        title = 'ERROR_WINHTTP_TIMEOUT'
        message = 'The request has timed out.'
    elif error_id == 12180:
        title = 'ERROR_WINHTTP_AUTODETECTION_FAILED'
        message = 'Returned by WinHttpDetectAutoProxyConfigUrl if WinHTTP was unable to discover the URL of the Proxy Auto-Configuration (PAC) file.'
    elif error_id == 12166:
        title = 'ERROR_WINHTTP_BAD_AUTO_PROXY_SCRIPT'
        message = 'An error occurred executing the script code in the Proxy Auto-Configuration (PAC) file.'
    elif error_id == 12178:
        title = 'ERROR_WINHTTP_AUTO_PROXY_SERVICE_ERROR'
        message = 'Returned by WinHttpGetProxyForUrl when a proxy for the specified URL cannot be located.'
    elif error_id == 12103:
        title = 'ERROR_WINHTTP_CANNOT_CALL_AFTER_OPEN'
        message = 'Returned by the HttpRequest object if a specified option cannot be requested after the Open method has been called.'
    elif error_id == 12102:
        title = 'ERROR_WINHTTP_CANNOT_CALL_AFTER_SEND'
        message = 'Returned by the HttpRequest object if a requested operation cannot be performed after calling the Send method.'
    elif error_id == 12100:
        title = 'ERROR_WINHTTP_CANNOT_CALL_BEFORE_OPEN'
        message = 'Returned by the HttpRequest object if a requested operation cannot be performed before calling the Open method.'
    elif error_id == 12101:
        title = 'ERROR_WINHTTP_CANNOT_CALL_BEFORE_SEND'
        message = 'Returned by the HttpRequest object if a requested operation cannot be performed before calling the Send method.'
    elif error_id == 12183:
        title = 'ERROR_WINHTTP_CHUNKED_ENCODING_HEADER_SIZE_OVERFLOW'
        message = 'Returned by WinHttpReceiveResponse when an overflow condition is encountered in the course of parsing chunked encoding.'
    elif error_id == 12044:
        title = 'ERROR_WINHTTP_CLIENT_AUTH_CERT_NEEDED'
        message = 'Returned by WinHttpReceiveResponse when the server requests client authentication.'
    elif error_id == 12030:
        title = 'ERROR_WINHTTP_CONNECTION_ERR'
        message = 'The connection with the server has been reset or terminated, or an incompatible SSL protocol was encountered. For example, WinHTTP version 5.1 does not support SSL2 unless the client specifically enables it.'
    elif error_id == 12155:
        title = 'ERROR_WINHTTP_HEADER_ALREADY_EXISTS'
        message = 'Obsolete; no longer used.'
    elif error_id == 12181:
        title = 'ERROR_WINHTTP_HEADER_COUNT_EXCEEDED'
        message = 'Returned by WinHttpReceiveResponse when a larger number of headers were present in a response than WinHTTP could receive.'
    elif error_id == 12150:
        title = 'ERROR_WINHTTP_HEADER_NOT_FOUND'
        message = 'The requested header cannot be located.'
    elif error_id == 12182:
        title = 'ERROR_WINHTTP_HEADER_SIZE_OVERFLOW'
        message = 'Returned by WinHttpReceiveResponse when the size of headers received exceeds the limit for the request handle.'
    elif error_id == 12019:
        title = 'ERROR_WINHTTP_INCORRECT_HANDLE_STATE'
        message = 'The requested operation cannot be carried out because the handle supplied is not in the correct state.'
    elif error_id == 12018:
        title = 'ERROR_WINHTTP_INCORRECT_HANDLE_TYPE'
        message = 'The type of handle supplied is incorrect for this operation.'
    elif error_id == 12004:
        title = 'ERROR_WINHTTP_INTERNAL_ERROR'
        message = 'An internal error has occurred.'
    elif error_id == 12009:
        title = 'ERROR_WINHTTP_INVALID_OPTION'
        message = 'A request to WinHttpQueryOption or WinHttpSetOption specified an invalid option value.'
    elif error_id == 12154:
        title = 'ERROR_WINHTTP_INVALID_QUERY_REQUEST'
        message = 'Obsolete; no longer used.'
    elif error_id == 12152:
        title = 'ERROR_WINHTTP_INVALID_SERVER_RESPONSE'
        message = 'The server response cannot be parsed.'
    elif error_id == 12005:
        title = 'ERROR_WINHTTP_INVALID_URL'
        message = 'The URL is not valid.'
    elif error_id == 12015:
        title = 'ERROR_WINHTTP_LOGIN_FAILURE'
        message = 'The login attempt failed. When this error is encountered, the request handle should be closed with WinHttpCloseHandle. A new request handle must be created before retrying the function that originally produced this error.'
    elif error_id == 12172:
        title = 'ERROR_WINHTTP_NOT_INITIALIZED'
        message = 'Obsolete; no longer used.'
    elif error_id == 12017:
        title = 'ERROR_WINHTTP_OPERATION_CANCELLED'
        message = 'The operation was canceled, usually because the handle on which the request was operating was closed before the operation completed.'
    elif error_id == 12011:
        title = 'ERROR_WINHTTP_OPTION_NOT_SETTABLE'
        message = 'The requested option cannot be set, only queried.'
    elif error_id == 12001:
        title = 'ERROR_WINHTTP_OUT_OF_HANDLES'
        message = 'Obsolete; no longer used.'
    elif error_id == 12156:
        title = 'ERROR_WINHTTP_REDIRECT_FAILED'
        message = 'The redirection failed because either the scheme changed or all attempts made to redirect failed (default is five attempts).'
    elif error_id == 12032:
        title = 'ERROR_WINHTTP_RESEND_REQUEST'
        message = 'The WinHTTP function failed. The desired function can be retried on the same request handle.'
    elif error_id == 12184:
        title = 'ERROR_WINHTTP_RESPONSE_DRAIN_OVERFLOW'
        message = 'Returned when an incoming response exceeds an internal WinHTTP size limit.'
    elif error_id == 12177:
        title = 'ERROR_WINHTTP_SCRIPT_EXECUTION_ERROR'
        message = 'An error was encountered while executing a script.'
    elif error_id == 12038:
        title = 'ERROR_WINHTTP_SECURE_CERT_CN_INVALID'
        message = 'Returned when a certificate CN name does not match the passed value (equivalent to a CERT_E_CN_NO_MATCH error).'
    elif error_id == 12037:
        title = 'ERROR_WINHTTP_SECURE_CERT_DATE_INVALID'
        message = 'Indicates that a required certificate is not within its validity period when verifying against the current system clock or the timestamp in the signed file, or that the validity periods of the certification chain do not nest correctly (equivalent to a CERT_E_EXPIRED or a CERT_E_VALIDITYPERIODNESTING error).'
    elif error_id == 12057:
        title = 'ERROR_WINHTTP_SECURE_CERT_REV_FAILED'
        message = 'Indicates that revocation cannot be checked because the revocation server was offline (equivalent to CRYPT_E_REVOCATION_OFFLINE).'
    elif error_id == 12170:
        title = 'ERROR_WINHTTP_SECURE_CERT_REVOKED'
        message = 'Indicates that a certificate has been revoked (equivalent to CRYPT_E_REVOKED).'
    elif error_id == 12179:
        title = 'ERROR_WINHTTP_SECURE_CERT_WRONG_USAGE'
        message = 'Indicates that a certificate is not valid for the requested usage (equivalent to CERT_E_WRONG_USAGE).'
    elif error_id == 12157:
        title = 'ERROR_WINHTTP_SECURE_CHANNEL_ERROR'
        message = 'Indicates that an error occurred having to do with a secure channel (equivalent to error codes that begin with "SEC_E_" and "SEC_I_" listed in the "winerror.h" header file).'
    elif error_id == 12175:
        title = 'ERROR_WINHTTP_SECURE_FAILURE'
        message = 'One or more errors were found in the Secure Sockets Layer (SSL) certificate sent by the server. To determine what type of error was encountered, check for a WINHTTP_CALLBACK_STATUS_SECURE_FAILURE notification in a status callback function. For more information, see WINHTTP_STATUS_CALLBACK.'
    elif error_id == 12045:
        title = 'ERROR_WINHTTP_SECURE_INVALID_CA'
        message = 'Indicates that a certificate chain was processed, but terminated in a root certificate that is not trusted by the trust provider (equivalent to CERT_E_UNTRUSTEDROOT).'
    elif error_id == 12169:
        title = 'ERROR_WINHTTP_SECURE_INVALID_CERT'
        message = 'Indicates that a certificate is invalid (equivalent to errors such as CERT_E_ROLE, CERT_E_PATHLENCONST, CERT_E_CRITICAL, CERT_E_PURPOSE, CERT_E_ISSUERCHAINING, CERT_E_MALFORMED and CERT_E_CHAINING).'
    elif error_id == 12012:
        title = 'ERROR_WINHTTP_SHUTDOWN'
        message = 'The WinHTTP function support is being shut down or unloaded.'
    elif error_id == 12176:
        title = 'ERROR_WINHTTP_UNHANDLED_SCRIPT_TYPE'
        message = 'The script type is not supported.'
    elif error_id == 12006:
        title = 'ERROR_WINHTTP_UNRECOGNIZED_SCHEME'
        message = 'The URL specified a scheme other than \"http:\" or \"https:\".'
    elif error_id == 5:
        title = 'ERROR_ACCESS_DENIED'
        message = 'Access is denied.'
    elif error_id == 6:
        title = 'ERROR_INVALID_HANDLE'
        message = 'The handle is invalid.'
    else:
        title = 'UNKNOWN'
        message = 'unknown'

    msg_max_len = 90
    msg_list = [message[i:i + msg_max_len] for i in range(0, len(message), msg_max_len)]

    print(' ' * alignment + '    => %s' % title)
    for msg in msg_list:
        print(' ' * alignment + '       %s' % msg)
    raise RuntimeError(f"{funcName} failed with error code {error_id}")


def resolve_proxy_with_pac(destination_url, pac_url):
    """Uses WinHTTP to resolve the proxy for the given URL using the PAC file."""
    winhttp = ctypes.windll.LoadLibrary("winhttp.dll")

    print("Platform", "supported" if winhttp.WinHttpCheckPlatform() else "unsupported")

    # Initialize WinHTTP session
    hSession = winhttp.WinHttpOpen(
        ctypes.c_wchar_p("PacTest"),  # user agent string
        WINHTTP_ACCESS_TYPE_NO_PROXY,
        WINHTTP_NO_PROXY_NAME,
        WINHTTP_NO_PROXY_BYPASS,
        WINHTTP_FLAG_ASYNC,
    )
    print("Session created", hSession)
    if not hSession:
        showLastError("WinHttpOpen")

    # force clear cache
    result = winhttp.WinHttpResetAutoProxy(
        hSession,
        WINHTTP_RESET_NOTIFY_NETWORK_CHANGED | WINHTTP_RESET_OUT_OF_PROC | WINHTTP_RESET_ALL,
    )
    print("Clearing Cache", "successfull" if result==0 else f"failed with code {result}")

    try:
        print("pac", pac_url, "dest", destination_url)

        auto_proxy_options = WINHTTP_AUTOPROXY_OPTIONS()
        auto_proxy_options.dwFlags = WINHTTP_AUTOPROXY_CONFIG_URL
        auto_proxy_options.dwAutoDetectFlags = 0
        auto_proxy_options.fAutoLogonIfChallenged = False
        auto_proxy_options.lpszAutoConfigUrl = ctypes.wintypes.LPCWSTR(pac_url)

        proxy_info = WINHTTP_PROXY_INFO()

        # Call WinHttpGetProxyForUrl
        result = winhttp.WinHttpGetProxyForUrl(
            hSession,
            ctypes.wintypes.LPCWSTR(destination_url),
            ctypes.byref(auto_proxy_options),
            ctypes.byref(proxy_info),
        )

        if not result:
            showLastError("WinHttpGetProxyForUrl")

        # Extract the proxy string from proxy_info
        proxy = proxy_info.lpszProxy if proxy_info.lpszProxy else "<no proxy>"
        return proxy

    finally:
        # Properly close the WinHTTP session handle
        winhttp.WinHttpCloseHandle(hSession)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI app to resolve proxies using a PAC file.")
    parser.add_argument("pac_file", help="Path to the PAC file.")
    parser.add_argument("destination_url", help="Destination URL to resolve the proxy for.")

    args = parser.parse_args()
    pac_file_path = args.pac_file
    destination_url = "https://" + args.destination_url

    if not os.path.exists(pac_file_path):
        print("Error: PAC file does not exist.")
        exit(1)

    # Start the webserver in a separate thread
    threading.Thread(target=start_webserver, daemon=True).start()
    pac_url = f"http://127.0.0.1:8080/pac/{os.path.basename(pac_file_path)}"

    # wait for flask to start
    wait_for_server("http://127.0.0.1:8080/up")
    time.sleep(30)

    try:
        proxy = resolve_proxy_with_pac(destination_url, pac_url)
        print(f"Resolved proxy: {proxy}")
    except Exception as e:
        print(f"Error: {e}")
