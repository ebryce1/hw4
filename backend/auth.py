"""Password hashing and verification.

Scheme: pbkdf2_sha256, stored as "pbkdf2_sha256$<salt>$<hex digest>".
This exact format and iteration count must stay fixed: signup hashes with it,
login re-hashes a login attempt the same way and compares. Nothing is ever
decrypted back into a password.
"""

import hashlib
import hmac
import secrets

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 120_000  # Matches the iteration count baked into the seed database's hashes.
SALT_BYTES = 16


def hash_password(password: str) -> str:
    """Hash a new password for signup. Generates a fresh random salt."""
    salt = secrets.token_hex(SALT_BYTES)
    digest = _derive(password, salt)
    return f"{ALGORITHM}${salt}${digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Check a login attempt against a stored hash.

    Reads the salt out of the stored string, re-hashes the attempt with that
    same salt (never generates a new one here), and compares digests in
    constant time so a timing attack can't leak how close a guess was.
    """
    try:
        algorithm, salt, stored_digest = stored_hash.split("$", 2)
    except ValueError:
        return False
    if algorithm != ALGORITHM:
        return False
    candidate_digest = _derive(password, salt)
    return hmac.compare_digest(candidate_digest, stored_digest)


def _derive(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), ITERATIONS
    ).hex()
