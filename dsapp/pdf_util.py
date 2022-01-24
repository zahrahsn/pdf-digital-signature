import datetime
import io
import os.path
import tempfile
import time
from itertools import groupby
import fitz
from PIL import Image
from PyPDF2 import PdfFileReader
from PyPDF2.pdf import PageObject, PdfFileWriter
from pyhanko import stamp
from pyhanko.sign import signers, fields
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign.fields import SigSeedSubFilter
from pyhanko.sign.general import load_cert_from_pemder
from pyhanko_certvalidator import ValidationContext
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from digitalsignature.settings import BASE_DIR
from dsapp.models import Signature

SIGN_PDF_SIZE = (1000, 700)


def has_transparency(img):
    if img.mode == "P":
        transparent = img.info.get("transparency", -1)
        for _, index in img.getcolors():
            if index == transparent:
                return True
    elif img.mode == "RGBA":
        extrema = img.getextrema()
        if extrema[3][0] < 255:
            return True
    return False


def add_img_background(img_file):
    img_file.seek(0)
    im = Image.open(img_file)
    if has_transparency(im):
        new_image = Image.new("RGBA", im.size, "WHITE")
        new_image.paste(im, (0, 0), im)
        new_image = new_image.convert('RGB')
        img_byte_arr = io.BytesIO()
        new_image.save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()
    else:
        img_file.seek(0)
        return img_file.read()


def jpeg_to_pdf(img_byte):
    img_file = Image.open(io.BytesIO(img_byte))
    img_byte_arr = io.BytesIO()
    new_im = Image.new('RGB', (img_file.width, img_file.height), "WHITE")
    new_im.paste(img_file, (0, 0))
    new_im.save(img_byte_arr, format='PDF')
    return img_byte_arr.getvalue()


def resize_pdf_signature(s_pdf):
    page = s_pdf.getPage(0)
    w = page.mediaBox.getWidth()
    h = page.mediaBox.getHeight()
    w_scale_factor = SIGN_PDF_SIZE[0] / w
    y_move_factor = SIGN_PDF_SIZE[1] - (h * w_scale_factor)
    writer = PdfFileWriter()
    writer.addBlankPage(width=SIGN_PDF_SIZE[0], height=SIGN_PDF_SIZE[1])
    writer.getPage(0).mergeScaledTranslatedPage(
        page, w_scale_factor, 0, y_move_factor
    )
    output = io.BytesIO()
    writer.write(output)
    return output


def add_data_to_signature(signature_pdf, **kwargs):
    signature_pdf = PdfFileReader(open(signature_pdf, "rb"))
    signature_pdf = PdfFileReader(resize_pdf_signature(signature_pdf))
    sign_print = io.BytesIO()
    signature_page: PageObject = signature_pdf.getPage(0)
    canvas_height = 200
    canvas_width = signature_page.mediaBox[2]
    can = canvas.Canvas(sign_print, pagesize=(canvas_width, canvas_height))
    can.setFillColorRGB(*colors.black.rgb(), alpha=0.7)
    can.rect(0, 0, canvas_width, canvas_height, fill=1)
    text_object = can.beginText()
    text_object.setFont('Times-Roman', 30)
    text_object.setTextOrigin(10, 160)
    text_object.setFillColorRGB(*colors.yellow.rgb(), alpha=1)
    text_object.textLine(f'Signer: {kwargs.get("signer_name")}')
    text_object.textLine(f'Time: {kwargs.get("timestamp")}')
    text_object.textLine(f'Serial: {kwargs.get("serial")}')
    text_object.textLine(f'SHA1 Fingerprint: {kwargs.get("sha1fp")}')
    text_object.textLine(f'Signature Algorithm: {kwargs.get("algo")}')
    can.drawText(text_object)
    can.showPage()
    can.save()
    sign_print.seek(0)
    text_pdf = PdfFileReader(sign_print)
    signature_page = signature_pdf.getPage(0)
    signature_page.mergeScaledTranslatedPage(
        text_pdf.getPage(0), 1, 0, 0,
        expand=True
    )
    writer = PdfFileWriter()
    writer.addPage(signature_page)
    output = io.BytesIO()
    writer.write(output)
    return output


def get_signature_locations(pdf_in, signs):
    with open(pdf_in, 'rb') as fh:
        out_file = io.BytesIO(fh.read())
    file_handle = fitz.open(stream=out_file.getvalue(), filetype="pdf")
    pages_rects = {}
    for page, signs_list in groupby(signs, key=lambda x: x['page']):
        page_num = int(page.replace("page-", ""))
        signs_list = list(signs_list)
        html_page_width = signs_list[0]['page_width']
        html_page_height = signs_list[0]['page_height']
        c_page = file_handle[page_num - 1]
        pix = c_page.getPixmap(alpha=True)
        point_to_px = pix.xres / 72
        px_to_point = 72 / pix.xres
        h_px = pix.height * point_to_px
        w_px = pix.width * point_to_px
        aspect_ratio = (w_px / html_page_width, h_px / html_page_height)
        rects = []
        for s in signs_list:
            sign_left = int(s['sign_left'] * aspect_ratio[0] * px_to_point)
            sign_width = int(s['sign_width'] * aspect_ratio[0] * px_to_point)
            sign_height = int(s['sign_height'] * aspect_ratio[1] * px_to_point)
            sign_top = pix.height - (int(s['sign_top'] * aspect_ratio[1] * px_to_point) + sign_height)
            sign_bottom_right_x = sign_left + sign_width
            if sign_bottom_right_x > c_page.CropBox[2]:
                sign_bottom_right_x = c_page.CropBox[2]
                sign_left = sign_bottom_right_x - sign_width
            sign_bottom_right_y = sign_top + sign_height
            if sign_bottom_right_y > c_page.CropBox[3]:
                sign_bottom_right_y = c_page.CropBox[3]
                sign_top = sign_bottom_right_y - sign_height
            rects.append(
                (sign_left, sign_top, sign_bottom_right_x, sign_bottom_right_y)
            )
        pages_rects[page_num] = rects
    return pages_rects


def sign_pdf(pdf_in, signs, user_sign: Signature, sign_pass):
    page_rects = get_signature_locations(pdf_in, signs)
    signer = signers.SimpleSigner.load(
        user_sign.privateKey.path,
        user_sign.certificate.path,
        ca_chain_files=(os.path.join(BASE_DIR, "site_cert.pem"),),
        key_passphrase=str.encode(sign_pass)
    )
    inf = open(pdf_in, 'rb')

    for page, rects in page_rects.items():
        for rect in rects:
            w = IncrementalPdfFileWriter(inf)
            s_filed_name = f'Signature_{current_milli_time()}'
            fields.append_signature_field(
                w, sig_field_spec=fields.SigFieldSpec(
                    s_filed_name,
                    on_page=page - 1,
                    box=rect
                )
            )
            user_cert = load_cert_from_pemder(user_sign.certificate.path)
            root_cert = load_cert_from_pemder(os.path.join(BASE_DIR, "site_cert.pem"))
            vc = ValidationContext([user_cert, root_cert])
            meta = signers.PdfSignatureMetadata(
                field_name=s_filed_name,
                subfilter=SigSeedSubFilter.PADES,
                signer_key_usage={"digital_signature"},
                embed_validation_info=True,
                validation_context=vc
            )
            pdf_signer = signers.PdfSigner(
                meta, signer=signer
            )
            final_stamp_file = add_data_to_signature(
                user_sign.pdf.path,
                signer_name=dict(signer.signing_cert.subject.native)['common_name'],
                timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%m"),
                serial=str(signer.signing_cert.serial_number),
                sha1fp=signer.signing_cert.sha1_fingerprint,
                algo=signer.signing_cert.signature_algo
            )
            if os.name == 'nt':
                delete = False
            else:
                delete = True
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=delete) as tmp:
                tmp.write(final_stamp_file.getvalue())
                sign_stamp_style = stamp.StaticStampStyle().from_pdf_file(tmp.name, border_width=0)
                pdf_signer.stamp_style = sign_stamp_style
                inf = pdf_signer.sign_pdf(w)
    with open(pdf_in, "wb") as f:
        f.write(inf.getbuffer())


def current_milli_time():
    return round(time.time() * 1000)
