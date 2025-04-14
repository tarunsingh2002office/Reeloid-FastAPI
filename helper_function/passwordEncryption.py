import bcrypt


def passwordEncryption(password):
    try:
        bytesPassword = password.encode("utf-8")
        salt = bcrypt.gensalt()#default rounds=12
        
        hashedPassword = bcrypt.hashpw(bytesPassword, salt)
        if not hashedPassword:
            raise ValueError("password Encryption problem")
        return hashedPassword.decode("utf-8")
    except Exception as err:
        print(err,"err")
        raise ValueError(str(err))
