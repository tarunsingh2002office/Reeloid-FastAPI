import bcrypt


def verifyPassword(password, hashedPassword):
    try:
        is_Verified = bcrypt.checkpw(
            password.encode("utf-8"), hashedPassword.encode("utf-8")
        )

        if not is_Verified:
            raise ValueError("incorrect password")
        return is_Verified
    except Exception as err:
        raise ValueError(str(err))
