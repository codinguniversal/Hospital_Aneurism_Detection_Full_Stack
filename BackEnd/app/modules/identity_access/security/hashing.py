import bcrypt


def get_password_hash(password: str) -> str:
    """
    Hashes a plain-text password using a secure, randomly generated salt.
    Converts the output byte-string into a clean UTF-8 string for safe storage in MongoDB.
    """
    #Convert plain-text string into bytes
    password_bytes = password.encode('utf-8')
    
    #Generate a random salt and hash the password (default 12 rounds of work factor)
    hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    
    # Decode back to a readable string format to persist cleanly in MongoDB
    return hashed_bytes.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compares a plain-text password against a stored hash value safely 
    to see if they match. Protects against timing attacks.
    """
    try:
        # Convert both strings back to raw bytes for cryptographic evaluation
        plain_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        
        # Verify if the plain bytes compute to the exact same hash structure
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except Exception:
        # If the hash string in DB is malformed or corrupted, fail closed safely
        return False