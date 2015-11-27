"""
Load RSA keys for encryption/decryption/sign/verify.
"""
from ldap3 import *
import json
import base64
import log
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_der_public_key, load_pem_private_key
from cryptography.hazmat.primitives import hashes

def get_cert(email, dump=False):
    """
    Get E-cert from HKPost LDAP server
    """
    # Connect to server
    server = Server('ldap1.hongkongpost.gov.hk', get_info=ALL)
    conn = Connection(server, auto_bind=True)
    conn.start_tls()
    # Get RSA cert
    conn.search('o=hongkong post e-cert (personal),c=hk', '(sn='+email+'*)')
    a = json.loads(conn.entries[-1].entry_to_json())['dn']
    OU = a[a.find('OU=')+3:a.find('OU=')+13]
    conn.search('EMAIL='+email+',OU='+str(OU)+
                ',o=hongkong post e-cert (personal),c=hk',
                '(objectclass=*)', search_scope=LEVEL,
                dereference_aliases=DEREF_BASE,
                attributes=[ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES])
    cert = conn.entries[0].entry_get_raw_attribute("userCertificate;binary")[0]
    # Cert info
    if dump:
        print(conn.entries[0].entry_get_dn())
        print(base64.b64encode(cert))
    # get x509 der public
    pub_key = x509.load_der_x509_certificate(cert, default_backend()).public_key()
    return pub_key

from cryptography.hazmat.primitives import serialization
def load_public_cert_from_file(filename):
    """
    Load pem public key from file
    """
    try:
        with open(filename, "rb") as key_file:
            public_key = serialization.load_pem_public_key(
                    key_file.read(),
                    backend=default_backend()
            )
            return public_key
    except Exception as e:
        log.print_exception(e)
        log.print_error("error", "failed to open file '%s'" % (r.text))
        return False

def load_private_cert_from_file(filename):
    '''
    Load private cert form file
    '''
    with open(filename, 'rb') as f:
        pem_data = f.read()
        key = load_pem_private_key(pem_data, password=None, backend=default_backend())
        return key

def encrypt_rsa(message, pub_key):
    cipher = pub_key.encrypt(message, padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None))
    return cipher

#openssl x509 -in cert -inform der -noout -pubkey > a.pem

def decrypt_rsa(data, key):
    plain = key.decrypt(data, padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None))
    return plain

def sign_rsa(data, private_key):
    signer = private_key.signer(
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256())
    signer.update(data)
    signature = signer.finalize()
    return signature

def verify_rsa(data, signature, public_key):
    verifier = public_key.verifier(
            signature,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256())
    verifier.update(data)
    try:
        verifier.verify()
    except:
        return False
    return True

if __name__ == "__main__":
    '''
    For testing
    '''
    # Test encryption
    public_key = get_cert("oneonestar@gmail.com")
    cipher = encrypt_rsa(b'test', public_key)
    private_key = load_private_cert_from_file("/home/star/.ssh/me.key.pem2")
    print(decrypt_rsa(cipher, private_key))

    # Test signature
    data = b'abcdefg'
    signature = sign_rsa(data, private_key)
    print("signature: ", signature)
    data = b'abc'
    print("verify: ", verify_rsa(data, signature, public_key))
