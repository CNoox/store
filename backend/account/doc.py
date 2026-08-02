one = """
Verify the OTP code and authenticate the user.

This endpoint validates the OTP sent to the user's email address.
If the OTP is valid, the user is authenticated and an access token is returned.
If the user does not already exist, a new account is created automatically.

Request:
    POST /api/account/otp/

Request Body:
    email (str): User's email address.
    otp (str): One-time password sent to the email.

Responses:
    200:
        Existing user authenticated successfully.

        {
            "token": "<access_token>"
        }

    201:
        New user created and authenticated successfully.

        {
            "token": "<access_token>"
        }

    400:
        Invalid email or OTP.
"""