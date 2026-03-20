from django.urls import path

from .api_views import (ActivateInviteView, OwnerProfileView, ProfileView,
                        RequestCodeView, VerifyCodeView)
from .web_views import (login_view, logout_view, profile_view, resend_otp_view,
                        verify_view)

app_name = "users"

urlpatterns = [
    path("auth/request-code/", RequestCodeView.as_view(), name="request-code"),
    path("auth/verify-code/", VerifyCodeView.as_view(), name="verify-code"),
    # API
    path("api/profile/", ProfileView.as_view(), name="profile-api"),
    path("api/profile/activate-invite/", ActivateInviteView.as_view(), name="activate-invite"),
    path("api/profile/<int:user_id>/", OwnerProfileView.as_view(), name="owner-profile"),
    # WEB
    path("", login_view, name="login"),
    path("verify/", verify_view, name="verify"),
    path("resend/", resend_otp_view, name="resend"),
    path("profile/", profile_view, name="profile"),
    path("logout/", logout_view, name="logout"),
]
