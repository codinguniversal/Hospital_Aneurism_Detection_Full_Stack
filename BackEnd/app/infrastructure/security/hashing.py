import bcrypt


def get_password_hash(password: str) -> str:
    password_bytes = password.encode('utf-8')
    
    # gensalt() defaults to 2^12 = 4096 iterations of hashing, 
    # which slows down brute-force attacks while remaining fast enough for legitimate users.
    hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    
    return hashed_bytes.decode('utf-8') # all passwords stored in length of 60 characters in database, regardless of input length


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compares a plain-text password against a stored hash value safely 
    to see if they match. Protects against timing attacks.
    """
    try:
        plain_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        
        # verify if the plain bytes compute to the exact same hash structure
        return bcrypt.checkpw(plain_bytes, hashed_bytes) # this way the system give zero execution time clues
    
    except Exception:
        # if the hash string in DB is malformed or corrupted, fail closed safely
        return False