"""Web views for OTP authentication flow.
These views provide a minimal HTML authentication interface:
1. User submits a phone number.
2. System generates an OTP code.
3. User verifies the OTP.
4. JWT tokens are issued and stored in cookies."""
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .services import request_otp, verify_otp


def login_view(request):
    """Render login page where user enters phone number.
    Workflow:
    1. User submits phone number
    2. OTP is generated via request_otp service
    3. Phone number is stored in session
    4. User is redirected to OTP verification page"""
    if request.method == "POST":
        phone = request.POST.get("phone")  # Extract phone number from submitted form
        request_otp(phone)  # Trigger OTP generation
        request.session["phone"] = phone  # Save phone number in session
        return redirect("users:verify")  # Redirect user to verification page

    return render(request, "users/login.html")  # Render login template for GET request


def verify_view(request):
    """Render OTP verification page.
    Workflow:
    1. Phone number is retrieved from session
    2. User submits OTP code
    3. OTP is verified via verify_otp service
    4. JWT tokens are issued and stored in HTTP-only cookies
    5. User is redirected to profile page"""
    phone = request.session.get("phone")  # Filled form session
    if not phone:
        return redirect("users:login")

    if request.method == "POST":
        code = request.POST.get("code")
        tokens = verify_otp(phone, code)  # Verify OTP and save cookies
        response = redirect("users:profile")  # Redirect after successful authentication
        request.session["user_phone"] = phone
        response.set_cookie("access", tokens["access"], httponly=True, samesite="Lax")
        response.set_cookie("refresh", tokens["refresh"], httponly=True, samesite="Lax")

        del request.session["phone"]  # Delete phone form session

        return response

    return render(request, "users/verify.html", {"phone": phone})  # Render verification page


def profile_view(request):
    phone = request.session.get("user_phone")
    return HttpResponse(f"Profile page for {phone}")
