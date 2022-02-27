import os.path
import traceback

from django.core.files.base import ContentFile
import json

from dotenv import load_dotenv

from digitalsignature.settings import BASE_DIR
from dsapp import pdf_util
from dsapp.models import Document, SignStatus, Signature
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseServerError
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

from dsapp.verify_pdf import verify
from generate_cert import Certificate

load_dotenv()


def profile_page(request):
    try:
        signature = Signature.objects.get(originUser=request.user)
    except Signature.DoesNotExist:
        signature = None
    return render(request, 'profile.html', context={"signature": signature})


@csrf_exempt
def change_password(request):
    if request.method == 'POST':
        req_json = json.loads(request.body)
        current_pass = req_json["currentPass"]
        new_pass = req_json["newPass"]
        new_conf = req_json["newConf"]
        if not request.user.check_password(current_pass):
            return JsonResponse(
                {"status": 400, "message": "Current password is not correct!"}
            )
        if new_conf != new_pass:
            return JsonResponse(
                {"status": 400, "message": "Password and its confirmation don't match!"}
            )
        request.user.set_password(new_pass)
        request.user.save()
        return JsonResponse(
            {"status": 200, "message": "Password has been changes successfully!"}
        )


@csrf_exempt
def upload_sign(request):
    if request.method == 'POST':
        sign_image = request.FILES['signImg']
        sign_pass = request.POST['signPass']
        sign_pass_conf = request.POST['signPassConf']
        if sign_pass != sign_pass_conf:
            return JsonResponse(
                {"status": 400, "message": "Password and its confirmation don't match!"}
            )
        user_private_key, user_private_bytes = Certificate.generate_private_key(
            sign_pass)
        ca_private_key = Certificate.load_private_key(
            os.path.join(BASE_DIR, "site_key.pem"),
            os.getenv("CA_PASSPHRASE")
        )
        certificate = Certificate.generate_user_certificate(
            user_private_key,
            ca_private_key,
            request.user.email,
            request.user.first_name,
            request.user.last_name
        )
        pk_file = ContentFile(user_private_bytes)
        cert_file = ContentFile(certificate)
        jpeg_signature = pdf_util.add_img_background(sign_image.file)
        signature = Signature()
        signature.originUser = request.user
        signature.image = ContentFile(jpeg_signature, name="signature.jpg")
        signature.pdf = ContentFile(pdf_util.jpeg_to_pdf(jpeg_signature), name="signature.pdf")
        signature.privateKey.save("user_private_key.pem", pk_file)
        signature.certificate.save("cert.pem", cert_file)
        signature.save()
        return JsonResponse(
            {"status": 200, "message": "Your signature has been generated successfully."}
        )


def inbox_page(request):
    docs = Document.objects.filter(receiverUser=request.user)
    return render(request, 'inbox.html', context={'docs': docs})


@csrf_exempt
def login_request(request):
    if request.user.is_authenticated:
        return redirect("profile")
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f'you are now logged in as {username}.')
                return redirect("profile")

            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, 'Invalid username or password.')
    form = AuthenticationForm
    return render(request=request, template_name="login.html", context={"login_form": form})


def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("login")


def outbox(request):
    sents = Document.objects.filter(originUser=request.user)
    for s in sents:
        s.title = s.title.replace(f"_to_{s.receiverUser}", "")
    return render(request, 'outbox.html', context={'keys': sents})


@csrf_exempt
def senddoc(request):
    uploadedFile = request.FILES['file1']
    d = Document()
    d.originUser = request.user
    try:
        receiver = User.objects.get(email__exact=request.POST['email1'])
    except User.DoesNotExist:
        return HttpResponse(f"Couldn't find any user with email: {request.POST['email1']}")
    d.receiverUser = receiver
    d.title = uploadedFile.name
    status = SignStatus.objects.get(name="Unread")
    d.status = status
    d.path = uploadedFile
    d.save()
    return HttpResponse("Your document has been sent.")


@csrf_exempt
def signing_page(request):
    if request.method == 'POST':
        src_file = request.POST["pdfFile"]
        from_page = request.POST["fromPage"]
        try:
            user_sign = Signature.objects.get(originUser=request.user)
        except Signature.DoesNotExist:
            return HttpResponse(f"Couldn't find any signature for you")
        try:
            if from_page == 'inbox':
                pdfFile = Document.objects.get(receiverUser=request.user, title=src_file)
                pdfFile.status = SignStatus.objects.get(name="Read")
                pdfFile.save()
            else:
                pdfFile = Document.objects.get(originUser=request.user, title=src_file)
        except Document.DoesNotExist:
            return HttpResponse(f"Couldn't find the file")
        return render(
            request,
            'signing.html',
            context={
                "pdf_file": pdfFile,
                "sign": user_sign
            }
        )


@csrf_exempt
def apply_signature(request):
    try:
        if request.method == 'POST':
            try:
                user_sign = Signature.objects.get(originUser=request.user)
            except Signature.DoesNotExist:
                return HttpResponse("Couldn't find any signature for you")
            req_json = json.loads(request.body)
            signs = req_json["signs"]
            pdf_in = req_json["pdfFile"]
            sign_pass = req_json["signPass"]
            pdf_file = req_json["fileName"]
            pdf_util.sign_pdf(
                pdf_in, signs, user_sign, sign_pass
            )
            try:
                pdfFile = Document.objects.get(receiverUser=request.user, title=pdf_file)
                pdfFile.status = SignStatus.objects.get(name="Signed")
                pdfFile.save()
            except Document.DoesNotExist:
                return HttpResponse("Couldn't find the document.")
            return JsonResponse(
                {
                    "status": 200,
                    "message": "Your signature applied on the document."
                }
            )
    except AttributeError:
        return HttpResponseServerError("Signature password is not correct.")
    except Exception as ex:
        print(traceback.format_exc())
        return HttpResponseServerError(ex)


@csrf_exempt
def reject(request):
    if request.method == 'POST':
        req_json = json.loads(request.body)
        pdf_file = req_json["fileName"]
        try:
            pdfFile = Document.objects.get(receiverUser=request.user, title=pdf_file)
            pdfFile.status = SignStatus.objects.get(name="Rejected")
            pdfFile.save()
        except Document.DoesNotExist:
            return HttpResponse(f"Couldn't find the document.")
        return JsonResponse(
            {
                "status": 200,
                "message": "Signing request rejected successfully."
            }
        )


def verifying_page(request):
    return render(request, 'verify.html')


@csrf_exempt
def verify_signature(request):
    pdf_file = request.FILES["docFile"]
    try:
        signs = verify(pdf_file)
        return JsonResponse(
            {
                "status": 200,
                "signs": signs
            }
        )
    except Exception as ex:
        return HttpResponseServerError(f"Validation Faliure\n{ex}")
