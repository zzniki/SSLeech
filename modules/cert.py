import ssl
import socket
import OpenSSL
import datetime
import settings
import typing as typ
from threading import Thread
import time
import ctypes

def killThread(thread: Thread):
    if (not thread.is_alive()): return

    exc = ctypes.py_object(SystemExit)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread.ident), exc)

    if (res > 1):
        # If it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)

def sockConnectProc(sock: socket.socket, host: str, port: int):
    # This approach is used so the tool works with torify / torsocks

    try:
        sock.connect((host, port))
    except:
        sock = None

def getCert(host: str, port: int = 443) -> OpenSSL.crypto.X509:
    context = ssl.create_default_context()
    context.check_hostname = False

    sock = context.wrap_socket(
        socket.socket(socket.AF_INET, socket.SOCK_STREAM),
        server_hostname=host)
    
    sock.settimeout((settings.TIMEOUT))

    p = Thread(target=sockConnectProc, args=(sock, host, port,))

    p.start()
    start = time.time()

    while (time.time() - start <= settings.TIMEOUT + .1):
        if (not p.is_alive()): break
        time.sleep(.1)
    else:
        killThread(p)

        raise TimeoutError("Timed out while connecting to " + str(host)  + ":" + str(port))

    if (sock == None):
        raise ConnectionError("Error connecting to " + str(host) + ":" + str(port))

    try:
        derCert = sock.getpeercert(True)
    except:
        raise Exception("Could not get certificate from " + str(host) + ":" + str(port))
    finally:
        sock.close()

    pemCert = ssl.DER_cert_to_PEM_cert(derCert)
    
    return OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, pemCert)

def getDomainsFromCert(cert: OpenSSL.crypto.X509) -> typ.List[str]:

    mainDomain = str(cert.get_subject().CN) # str just in case
    altDomains = []

    for i in range(cert.get_extension_count()):
        ext = cert.get_extension(i)
        if (ext.get_short_name().decode() == "subjectAltName"):
            altDomains = [d.split(":")[-1] for d in str(ext).split(",")]
            break

    altDomains.append(mainDomain)
    return list(set(altDomains))