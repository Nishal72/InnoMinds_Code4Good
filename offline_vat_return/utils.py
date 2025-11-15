from Crypto.Cipher import AES
import base64

AES_KEY = b"1234567812345678"    # 16 bytes
AES_IV  = b"1234567812345678"    # 16 bytes

def pad(s):
    return s + (16 - len(s) % 16) * chr(16 - len(s) % 16)

def unpad(s):
    return s[:-ord(s[len(s)-1:])]

def encrypt_message(plain_text: str):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    padded = pad(plain_text)
    encrypted_bytes = cipher.encrypt(padded.encode())
    return base64.b64encode(encrypted_bytes).decode()

def decrypt_message(enc_text: str):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    decoded = base64.b64decode(enc_text)
    decrypted = cipher.decrypt(decoded)
    return unpad(decrypted.decode())
