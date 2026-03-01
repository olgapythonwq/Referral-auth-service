from django.urls import path

from .views import RequestCodeView, VerifyCodeView, ProfileView, ActivateInviteView

app_name = "users"

urlpatterns = [
    path("auth/request-code/", RequestCodeView.as_view(), name="request-code",),
    path("auth/verify-code/", VerifyCodeView.as_view(), name="verify-code",),
    path("profile/", ProfileView.as_view(), name="profile",),
    path("profile/activate-invite/", ActivateInviteView.as_view(), name="activate-invite",),
]
