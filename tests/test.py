import datetime
from io import BytesIO

from PyPDF2 import PdfFileReader

from dsapp import pdf_util


def test_png_to_pdf():
    with open("signature.jpg", "rb") as img:
        image_file = BytesIO(img.read())
    jpeg_bytes = pdf_util.add_img_background(image_file)
    pdf_bytes = pdf_util.jpeg_to_pdf(jpeg_bytes)
    with open("signature.pdf", "wb") as pdf:
        pdf.write(pdf_bytes)


def test_create_signature_stamp():
    s = pdf_util.add_data_to_signature(
        "signature.pdf",
        signer_name="The Signer Name",
        timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%m"),
        serial="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        sha1fp="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        algo="algorithm"
    )
    with open("out.pdf", "wb") as out:
        out.write(s.getvalue())


def test_pdf_resize():
    signature_pdf = PdfFileReader(open('signature.pdf', "rb"))
    resized = pdf_util.resize_pdf_signature(signature_pdf)
    with open("resized.pdf", "wb") as out:
        out.write(resized.getvalue())
