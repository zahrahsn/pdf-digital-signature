from django.contrib import admin

from dsapp.models import SignStatus,Signature,Document
admin.site.register(SignStatus)
admin.site.register(Signature)
admin.site.register(Document)
