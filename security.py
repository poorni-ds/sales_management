import hashlib


def hash_password(plain_password: str) -> str:
    """
    Turn a plaintext password into a fixed-length hash before it's ever
    stored in the database. SHA-256 is used here so the project needs no
    extra dependency beyond the Python standard library.

    Note for later: for a real production system, prefer a
    password-specific algorithm with per-user salting (bcrypt or
    argon2) instead of a plain SHA-256 hash. SHA-256 is a big
    improvement over storing plaintext, which is the bar this
    project needs to clear.
    """
    return hashlib.sha256(plain_password.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Hash the typed password the same way and compare it to what's stored."""
    return hash_password(plain_password) == hashed_password
