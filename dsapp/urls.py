from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login_request, name='login'),
    path('profile/', views.profile_page, name='profile'),
    path('inbox/', views.inbox_page, name='inbox'),
    path('logout/', views.logout_request, name="logout"),
    path('outbox/', views.outbox, name='outbox'),
    path('senddoc/', views.senddoc, name='senddoc'),
    path('signing/', views.signing_page, name='signing'),
    path('changePass/', views.change_password, name='changePass'),
    path('uploadSign/', views.upload_sign, name='uploadSign'),
    path('apply_signature/', views.apply_signature, name='apply_signature'),
    path('reject/', views.reject, name='reject'),
    path('verify/', views.verifying_page, name='verify'),
    path('verify_signature/', views.verify_signature, name='verify_signature'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
