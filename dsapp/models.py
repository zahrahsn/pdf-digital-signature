from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE, DO_NOTHING, SET_NULL
import os


def user_directory_path(instance, filename):
    return os.path.join('documents', str(instance.originUser), filename)


def user_certificate_path(instance, filename):
    return os.path.join('certificates', str(instance.originUser), filename)


class SignStatus(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Signature(models.Model):
    originUser = models.ForeignKey(User, on_delete=CASCADE)
    pdf = models.FileField(upload_to=user_certificate_path, null=True)
    image = models.ImageField(upload_to=user_certificate_path, null=True)
    certificate = models.FileField(upload_to=user_certificate_path, null=True)
    privateKey = models.FileField(upload_to=user_certificate_path, null=True)

    def __str__(self):
        return self.originUser.username


class Document(models.Model):
    title = models.CharField(max_length=1000, default="Untitled")
    originUser = models.ForeignKey(User, on_delete=CASCADE)
    receiverUser = models.ForeignKey(
        User, on_delete=CASCADE, related_name='receiver_User')
    status = models.ForeignKey(SignStatus, on_delete=DO_NOTHING)
    signature = models.ForeignKey(
        Signature, on_delete=SET_NULL, blank=True, null=True)
    path = models.FileField(upload_to=user_directory_path, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
