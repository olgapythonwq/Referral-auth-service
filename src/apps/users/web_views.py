"""Web views for OTP authentication flow.
These views provide a minimal HTML authentication interface:
1. User submits a phone number.
2. System generates an OTP code (One-Time Password).
3. User enters OTP.
4. System verifies OTP and issues JWT tokens.
5. User accesses profile page"""
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework.exceptions import ValidationError

from .services import activate_invite, request_otp, verify_otp

# Get custom User model
User = get_user_model()


def login_view(request):
    """Render login page where user enters phone number.
    Workflow:
    1. User submits phone number
    2. OTP is generated via request_otp service
    3. Phone number is stored in session
    4. Initialize OTP attempts counter
    5. User is redirected to OTP verification page"""
    if request.method == "POST":
        phone = request.POST.get("phone")  # Extract phone number from submitted form
        request_otp(phone)  # Generate OTP and store it (DB + logs)
        request.session["phone"] = phone  # Save phone number in session
        request.session["otp_attempts"] = 0  # Initialize number of failed attempts

        return redirect("users:verify")  # Redirect user to OTP verification page

    return render(request, "users/login.html")  # Render login template for GET request


def verify_view(request):
    """Handle OTP verification.
    GET:
    1. Render OTP input form
    POST:
    1. Validate OTP
    2. On success:
        - issue JWT tokens
        - store them in cookies
        - redirect to profile
    3. On failure:
        - increment attempts counter
        - show error message
        - optionally show "Resend code" button"""
    phone = request.session.get("phone")  # Retrieve phone form session
    if not phone:  # If session expired or missing — redirect to login page
        return redirect("users:login")

    attempts = request.session.get("otp_attempts", 0)  # Get number of failed attempts (default = 0)

    if request.method == "POST":
        code = request.POST.get("code")  # Extract OTP code from form

        try:
            tokens = verify_otp(phone, code)  # Verify OTP and save cookies

        except ValidationError:
            attempts += 1  # Increment failed attempts counter
            request.session["otp_attempts"] = attempts

            return render(request, "users/verify.html", {
                "phone": phone,
                "error": "Invalid code. Please try again.",
                "show_resend": attempts >= 2,  # show resend after 2 failures
            },)  # Re-render page with error message

        # Successful authentication
        response = redirect("users:profile")  # Redirect to profile page
        request.session["user_phone"] = phone  # Save authenticated user phone in session
        # Store JWT tokens in HTTP-only cookies
        response.set_cookie("access", tokens["access"], httponly=True, samesite="Lax")
        response.set_cookie("refresh", tokens["refresh"], httponly=True, samesite="Lax")

        del request.session["phone"]  # Delete phone form session
        request.session.pop("otp_attempts", None)

        return response

    return render(request, "users/verify.html", {
        "phone": phone,
        "show_resend": attempts >= 2,
    })  # GET request — render page


def resend_otp_view(request):
    """Resend OTP code.
    1. Generates a NEW OTP (does not reuse old one)
    2. Keeps same phone from session
    3. Redirects back to verification page"""
    phone = request.session.get("phone")  # Get phone from session
    if not phone:
        return redirect("users:login")  # If no session — redirect to login page

    request_otp(phone)  # Generate new OTP

    return redirect("users:verify")  # Redirect back to verification page


def profile_view(request):
    """Display user profile and handle invite activation.
    GET:
        1. Show user data (phone, invite code, referrals)
    POST:
        1. Activate invite code
        2. Show success or error message"""
    phone = request.session.get("user_phone")  # Get phone from session
    if not phone:
        return redirect("users:login")  # If not authenticated — redirect to login page

    user = get_object_or_404(User, phone=phone)  # Fetch user from database

    error = None
    success = None

    if request.method == "POST":
        invite_code = request.POST.get("invite_code")  # Extract invite code from form

        try:
            activate_invite(user, invite_code)  # Try to activate invite code
            success = "Invite code activated!"

        except ValidationError as e:
            error = str(e)  # Convert error to readable string

    return render(request, "users/profile.html", {
        "user": user,
        "error": error,
        "success": success,
    },)  # Render profile page


def logout_view(request):
    """Log out user.
    1. Clear session data
    2. Remove JWT cookies
    3. Redirect to login page"""
    request.session.flush()  # Clear entire session

    response = redirect("users:login")  # Redirect to login page
    # Remove authentication cookies
    response.delete_cookie("access")
    response.delete_cookie("refresh")

    return response
