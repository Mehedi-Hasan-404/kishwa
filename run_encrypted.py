import os
import sys
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet, InvalidToken

def decrypt_and_run(enc_path: str, password: str):
    with open(enc_path, "rb") as f:
        data = f.read()

    salt = data[:16]
    token = data[16:]

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    fernet = Fernet(key)

    try:
        plaintext = fernet.decrypt(token)
    except InvalidToken:
        print("[✗] Wrong password or corrupted file. Aborting.")
        sys.exit(1)

    # Run decrypted code in-memory
    exec(compile(plaintext, enc_path, "exec"), {"__name__": "__main__"})

if __name__ == "__main__":
    password = os.environ.get("SCRIPT_PASSWORD", "").strip()
    if not password:
        print("[✗] SCRIPT_PASSWORD environment variable is not set.")
        sys.exit(1)

    enc_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generate_m3u.enc")
    if not os.path.exists(enc_file):
        print(f"[✗] Encrypted file not found: {enc_file}")
        sys.exit(1)

    print("[*] Decrypting and running script...")
    decrypt_and_run(enc_file, password)
