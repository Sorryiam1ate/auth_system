import bcrypt


def hash_password(password: str):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()


def check_password(password: str, hashed: str):
    if not hashed.startswith("$2b$") and not hashed.startswith("$2a$"):
        raise ValueError("Неверный формат хеша!")
    return bcrypt.checkpw(password.encode(), hashed.encode())
