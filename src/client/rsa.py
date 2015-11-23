from ldap3 import *
import json
import base64
import log
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_der_public_key, load_pem_private_key
from cryptography.hazmat.primitives import hashes

def get_cert(email):
    '''
    Get E-cert from HKPost LDAP server
    '''
    # Connect to server
    server = Server('ldap1.hongkongpost.gov.hk', get_info=ALL)
    conn = Connection(server, auto_bind=True)
    conn.start_tls()
    # Get RSA cert
    conn.search('o=hongkong post e-cert (personal),c=hk', '(sn='+email+'*)')
    conn.entries[0]
    a = json.loads(conn.entries[-1].entry_to_json())['dn']
    OU = a[a.find('OU=')+3:a.find('OU=')+13]
    conn.search('EMAIL='+email+',OU='+str(OU)+',o=hongkong post e-cert (personal),c=hk', '(objectclass=*)', search_scope=1, dereference_aliases=2, attributes=[ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES])
    cert = conn.entries[0].entry_get_raw_attribute("userCertificate;binary")[0]
	# Cert info
    print(conn.entries[0].entry_get_dn())
    print(base64.b64encode(cert))
    # get x509 der public 
    pub_key = x509.load_der_x509_certificate(cert, default_backend()).public_key()
    return pub_key

from cryptography.hazmat.primitives import serialization
def get_cert_from_file(filename):
    try:
        with open(filename, "rb") as key_file:
            public_key = serialization.load_pem_public_key(
                    key_file.read(),
                    backend=default_backend()
            )
    except Exception as e:
        log.print_exception(e)
        log.print_error("error", "failed to open file '%s'" % (r.text))
        return False

def encrypt_rsa(message, pub_key):
	cipher = pub_key.encrypt(message, padding.OAEP(
		mgf=padding.MGF1(algorithm=hashes.SHA1()),
		algorithm=hashes.SHA1(),
		label=None))
	return cipher

#openssl x509 -in cert -inform der -noout -pubkey > a.pem

def decrypt_rsa(data, pem_private):
	key = load_pem_private_key(pem_private, password=None, backend=default_backend())
	plain = key.decrypt(data, padding.OAEP(
		mgf=padding.MGF1(algorithm=hashes.SHA1()),
		algorithm=hashes.SHA1(),
		label=None))
	return plain

if __name__ == "__main__":
    '''
    For testing
    '''
    cert = get_cert("oneonestar@gmail.com")
    cipher = encrypt_rsa(b'test', cert)
    with open('/home/star/.ssh/me.key.pem2', 'rb') as f:
        pem_data = f.read()
        print(decrypt_rsa(cipher, pem_data))
    get_cert_from_file("key/public_key.pem")
