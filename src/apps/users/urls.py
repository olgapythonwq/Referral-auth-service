from django.urls import path

from .apps import UsersConfig
from .views import RequestCodeView, VerifyCodeView

app_name = "users"

urlpatterns = [
    path("auth/request-code/", RequestCodeView.as_view(), name="request-code",),
    path("auth/verify-code/", VerifyCodeView.as_view(), name="verify-code",),
]
