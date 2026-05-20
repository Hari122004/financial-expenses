import jwt
import datetime

SECRET_KEY = "expense_tracker_secret"

# Generate Token
def generate_token(email):

    payload = {
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm="HS256"
    )

    return token

# Verify Token
def verify_token(token):

    try:
        decoded = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"]
        )

        return decoded

    except:
        return None