import datetime
import io
import os
import pathlib
import shutil
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.x509 import load_pem_x509_certificate, KeyUsage
from cryptography.x509.oid import NameOID
from dotenv import load_dotenv

from digitalsignature.settings import BASE_DIR

load_dotenv()

ROOT_VALIDITY = 30
USER_VALIDITY = 2


class Certificate:
    @staticmethod
    def generate_private_key(passphrase, path=None):
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        private_bytes = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.BestAvailableEncryption(str.encode(passphrase))
        )
        if path is None:
            return key, private_bytes
        else:
            with open(path, "wb") as out:
                out.write(private_bytes)

    @staticmethod
    def load_private_key(path, passphrase):
        with open(path, "rb") as f:
            return load_pem_private_key(f.read(), str.encode(passphrase))

    @staticmethod
    def load_certificate(path):
        with open(path, "rb") as f:
            return load_pem_x509_certificate(f.read(), default_backend())

    @staticmethod
    def save_certificate(certificate, path):
        with open(path, "wb") as f:
            f.write(certificate.public_bytes(serialization.Encoding.PEM))

    @staticmethod
    def generate_root_certificate(private_key, country, province, city, organization, domain):
        """
        Generates a root CA by given information.
        :param private_key: private key for signing the certificate.
        :param country: CA's country.
        :param province: CA's province.
        :param city: CA's city.
        :param organization: CA's organization.
        :param domain: CA's domain.
        :return: the CA certificate.
        """
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, country),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, province),
            x509.NameAttribute(NameOID.LOCALITY_NAME, city),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
            x509.NameAttribute(NameOID.COMMON_NAME, domain),
        ])
        basic_constraints = x509.BasicConstraints(ca=True, path_length=1)
        return x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=ROOT_VALIDITY * 365)
        ).add_extension(
            basic_constraints, True
        ).sign(private_key, hashes.SHA256(), default_backend())

    @staticmethod
    def generate_user_certificate(user_pk, ca_pk, email, first_name, last_name):
        """
        Generates a certificate and signs it by root CA.
        :param user_pk: The private key of the user.
        :param ca_pk: The private key of CA for signing the Certificate.
        :param email: user's Email.
        :param first_name: user's first name.
        :param last_name: user's last name.
        :return: The signed certificate.
        """
        root_cert = Certificate.load_certificate(os.path.join(BASE_DIR, "site_cert.pem"))
        authority_key = x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_pk.public_key())
        user_info = x509.Name([
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, email),
            x509.NameAttribute(NameOID.GIVEN_NAME, first_name),
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, last_name),
            x509.NameAttribute(NameOID.COMMON_NAME, first_name + last_name),
        ])
        user_cert = x509.CertificateBuilder().subject_name(
            user_info
        ).issuer_name(
            root_cert.issuer
        ).public_key(
            user_pk.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=USER_VALIDITY * 365)
        ).add_extension(
            authority_key, True
        ).add_extension(
            x509.KeyUsage(
                key_cert_sign=True,
                crl_sign=True,
                digital_signature=True,
                content_commitment=False,
                key_encipherment=True,
                data_encipherment=False,
                key_agreement=True,
                encipher_only=False,
                decipher_only=False
            ),
            critical=False
        ).sign(ca_pk, hashes.SHA256(), default_backend())
        return user_cert.public_bytes(serialization.Encoding.PEM)


if __name__ == "__main__":
    key_file_path = os.path.join(BASE_DIR, "site_key.pem")
    cert_file_path = os.path.join(BASE_DIR, "site_cert.pem")
    if not Path(cert_file_path).is_file():
        if not Path(key_file_path).is_file():
            Certificate.generate_private_key(os.getenv("CA_PASSPHRASE"), path=key_file_path)
        pk = Certificate.load_private_key(key_file_path, os.getenv("CA_PASSPHRASE"))
        cert = Certificate.generate_root_certificate(
            pk,
            os.getenv("CA_COUNTRY"),
            os.getenv("CA_PROVINCE"),
            os.getenv("CA_CITY"),
            os.getenv("CA_ORG"),
            os.getenv("CA_DOMAIN")
        )
        Certificate.save_certificate(
            cert, cert_file_path
        )
