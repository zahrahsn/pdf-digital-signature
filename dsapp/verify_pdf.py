import os

from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.general import load_cert_from_pemder, KeyUsageConstraints
from pyhanko.sign.validation import validate_pdf_signature
from pyhanko_certvalidator import ValidationContext
from digitalsignature.settings import BASE_DIR


def verify(pdf_file):
    root_cert = load_cert_from_pemder(os.path.join(BASE_DIR, "site_cert.pem"))
    vc = ValidationContext(trust_roots=[root_cert])
    key_usage = KeyUsageConstraints(key_usage={'digital_signature'})
    r = PdfFileReader(pdf_file)
    signatures = r.embedded_signatures
    signs = []
    for sig in signatures:
        status = validate_pdf_signature(sig, vc, key_usage_settings=key_usage)
        print(status.pretty_print_details())
        signs.append(
            {
                'signer': dict(status.signing_cert.subject.native),
                'cert_issuer': dict(status.signing_cert.issuer.native),
                'intact': status.intact,
                'trusted': status.trusted,
                'datetime': status.signer_reported_dt.strftime("%d/%m/%Y, %H:%M:%S")
            }
        )
    return signs