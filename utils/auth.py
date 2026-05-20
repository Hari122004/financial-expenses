import bcrypt

# -----------------------------------
# HASH PASSWORD
# -----------------------------------
def hash_password(password):

    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    )

# -----------------------------------
# VERIFY PASSWORD
# -----------------------------------
def verify_password(password, hashed_password):

    return bcrypt.checkpw(
        password.encode(),
        hashed_password
    )