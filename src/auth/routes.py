from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from src.auth.dependencies import (
    RefreshTokenBearer,
    AccessTokenBearer,
    get_current_user,
    RoleChecker,
)
from src.auth.schemas import (
    PasswordResetConfirmModel,
    PasswordResetRequestModel,
    UserCreateModel,
    UserModel,
    UserLoginModel,
    UserBooksModel,
    EmailModel,
)
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.service import UserService
from src.config import Config
from src.db.main import get_session
from src.auth.utils import (
    create_access_token,
    create_url_safe_token,
    decode_url_safe_token,
    hash_password,
)
from datetime import timedelta, datetime
from fastapi.responses import JSONResponse
from src.db.redis import add_jti_to_blacklist
from src.errors import InvalidToken, UserNotFound
from src.mail import create_message, mail
from src.celery_tasks import send_email

auth_router = APIRouter()
user_service = UserService()
refresh_token_bearer = RefreshTokenBearer()
access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(allowed_roles=["admin", "user"])

REFRESH_TOKEN_EXPIRY = 2


@auth_router.post("/send_mail")
async def send_mail(emails: EmailModel):
    """
    Send welcome email to multiple recipients.

    This endpoint allows sending a welcome email to multiple email addresses.
    Emails are sent asynchronously using Celery for better performance.

    Args:
        emails (EmailModel): Contains a list of email addresses to send welcome emails to

    Returns:
        dict: Confirmation message that emails were queued for sending

    Note:
        This is a utility endpoint, typically used for testing email functionality.
    """
    emails = emails.addresses
    html = "<h1>Welcome to the app</h1>"
    subject = "Welcome to our app"
    # message = create_message(recipients=emails, subject="Welcome to the app", body=html)
    # await mail.send_message(message)
    # pakai celery untuk mengirim email di background
    send_email.delay(emails, subject, html)
    return {"message": "Email sent successfully."}


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user_account(
    user_create_data: UserCreateModel,
    # bg_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new user account.

    This endpoint allows new users to register by providing their personal
    information including email, password, first name, and last name.
    The email must be unique in the system.

    Args:
        user_create_data (UserCreateModel): User registration data

    Returns:
        UserModel: The newly created user account (without password)

    Raises:
        403: If a user with the provided email already exists
        500: If there is an internal server error during the creation (e.g., database issues, etc)
    """
    new_user = await user_service.create_user(user_create_data, session)
    token = create_url_safe_token({"email": new_user.email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"
    html = f"""
    <h1>Verify your Email</h1>
    <p>Please click this <a href="{link}">link</a> to verify your email</p>
    """
    # message = create_message(
    #     recipients=[new_user.email],
    #     subject="Verify Your Email",
    #     body=html_message,
    # )
    # await mail.send_message(message)
    # menggunakan background task agar response yang dikembalikan lebih cepat karena proses yang lama seperti mengirim email dilakukan setelah response dikembalikan ke user
    # bg_tasks.add_task(mail.send_message, message)
    emails = [new_user.email]
    subject = "Verify Your email"
    send_email.delay(emails, subject, html)
    return {
        "message": "Account Created! Check email to verify your account.",
        "user": new_user,
    }


@auth_router.get("/verify/{token}")
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    """
    Verify user email address using verification token.

    This endpoint verifies a user's email address by validating the token
    sent to their email during registration. Once verified, the user can
    access protected endpoints.

    Args:
        token (str): The verification token sent to user's email
        session (AsyncSession): Database session dependency

    Returns:
        dict: Confirmation message that account was verified successfully

    Raises:
        404: If the user associated with the token is not found
        500: If the token is invalid or verification process fails / if there is an internal server error during the verification (e.g., database issues, etc)
    """
    token_data = decode_url_safe_token(token)
    print("TOKEN_DATA:", token_data)
    user_email = token_data.get("email")
    if user_email:
        user = await user_service.get_user_by_email(user_email, session)
        if not user:
            raise UserNotFound()
        await user_service.update_user(user, {"is_verified": True}, session)
        return JSONResponse(
            content={"message": "Account verified successfully."},
            status_code=status.HTTP_200_OK,
        )
    raise HTTPException(
        detail="Error occured while verifying account.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@auth_router.post("/login")
async def login_user(
    login_data: UserLoginModel, session: AsyncSession = Depends(get_session)
):
    """
    Authenticate user and return access tokens.

    This endpoint authenticates a user using their email and password,
    returning both access and refresh tokens for subsequent API calls.

    Args:
        login_data (UserLoginModel): User login credentials (email and password)

    Returns:
        dict: Login response containing access_token, refresh_token, and user info

    Raises:
        400: If the provided email or password is invalid
        500: If there is an internal server error during the creation (e.g., database issues, etc)
    """
    user = await user_service.authenticate_user(login_data, session)
    access_token = create_access_token(
        user_data={"user_uid": str(user.uid), "email": user.email, "role": user.role}
    )
    refresh_token = create_access_token(
        user_data={"user_uid": str(user.uid), "email": user.email},
        refresh=True,
        expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
    )
    return JSONResponse(
        content={
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {"email": user.email, "uid": str(user.uid)},
        }
    )


@auth_router.post("/refresh-token")
async def get_new_access_token(
    token_details: dict = Depends(refresh_token_bearer),
):
    """
    Generate a new access token using a valid refresh token.

    This endpoint allows clients to obtain a new access token without
    requiring the user to log in again, using a valid refresh token.

    Args:
        token_details (dict): Refresh token details from the Authorization header

    Returns:
        dict: New access token

    Raises:
        401: If the refresh token is invalid or expired
        403: If the token is not a refresh token
    """
    expiry_timestamp = token_details["exp"]
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details["user"])
        return JSONResponse(content={"access_token": new_access_token})
    else:
        raise InvalidToken()


@auth_router.get("/me", response_model=UserBooksModel)
async def get_current_user(
    user=Depends(get_current_user), _: bool = Depends(role_checker)
):
    """
    Retrieve the current authenticated user's profile.

    This endpoint returns detailed information about the currently
    authenticated user, including their books and profile data.

    Args:
        user (UserModel): Access token details from the Authorization header

    Returns:
        UserBooksModel: Current user's profile information including their books

    Raises:
        401: If the access token is invalid or expired or if the token is not a access token
        403: If the user doesn't have sufficient permissions
        404: If the user is not found
        500: If there is an internal server error during the retrieval (e.g., database issues, etc)
    """
    return user


@auth_router.post("/logout")
async def revoke_token(
    token_details: dict = Depends(access_token_bearer),
):
    """
    Logout user and revoke the current access token.

    This endpoint logs out the current user by adding their access token
    to a blacklist, ensuring it cannot be used for future requests.

    Args:
        token_details (dict): Access token details from the Authorization header

    Returns:
        dict: Logout confirmation message

    Raises:
        401: If the access token is invalid or expired / if the token is not an access token
    """
    jti = token_details["jti"]
    await add_jti_to_blacklist(jti)
    return JSONResponse(
        content={"message": "Logged out successfully."}, status_code=status.HTTP_200_OK
    )


@auth_router.post("/password-reset-request")
async def password_reset_request(email_data: PasswordResetRequestModel):
    """
    Request password reset for a user account.

    This endpoint initiates the password reset process by sending a reset link
    to the user's email address. The link contains a secure token that allows
    the user to set a new password.

    Args:
        email_data (PasswordResetRequestModel): Contains the email address for password reset

    Returns:
        dict: Confirmation message that reset instructions were sent to email

    Note:
        Reset emails are sent asynchronously using Celery.
    """
    email = email_data.email
    token = create_url_safe_token({"email": email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"
    html = f"""
    <h1>Reset Your Password</h1>
    <p>Please click this <a href="{link}">link</a> to reset your password</p>
    """
    # message = create_message(
    #     recipients=[email],
    #     subject="Reset Your Password",
    #     body=html_message,
    # )
    # await mail.send_message(message)
    subject = "Reset Your Password"
    send_email.delay([email], subject, html)
    return JSONResponse(
        content={
            "message": "Please check your email for instructions to reset your password!"
        },
        status_code=status.HTTP_200_OK,
    )


@auth_router.post("/password-reset-confirm/{token}")
async def reset_account_password(
    token: str,
    passwords: PasswordResetConfirmModel,
    session: AsyncSession = Depends(get_session),
):
    """
    Confirm password reset and set new password.

    This endpoint completes the password reset process by validating the reset token
    and updating the user's password. The new password and confirmation must match.

    Args:
        token (str): The password reset token from the email link
        passwords (PasswordResetConfirmModel): Contains new_password and confirm_new_password
        session (AsyncSession): Database session dependency

    Returns:
        dict: Confirmation message that password was reset successfully

    Raises:
        400: If new password and confirm password don't match
        404: If the user associated with the token is not found
        500: If the token is invalid or reset process fails / if there is an internal server error during the password reset (e.g., database issues, etc)
    """
    new_password = passwords.new_password
    confirm_password = passwords.confirm_new_password
    if new_password != confirm_password:
        raise HTTPException(
            detail="New password and confirm new password do not match.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email")
    if user_email:
        user = await user_service.get_user_by_email(user_email, session)
        if not user:
            raise UserNotFound()
        password_hash = hash_password(new_password)
        await user_service.update_user(user, {"password_hash": password_hash}, session)
        return JSONResponse(
            content={"message": "Password reset Successfully."},
            status_code=status.HTTP_200_OK,
        )
    raise HTTPException(
        detail="Error occurred during password reset.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
