from fastapi import FastAPI, UploadFile, File, HTTPException
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad
from minio import Minio
from starlette.responses import StreamingResponse
import io
import urllib.parse

app = FastAPI()

# MinIO configuration
MINIO_ENDPOINT = 'your_minio_endpoint'
MINIO_ACCESS_KEY = 'your_minio_access_key'
MINIO_SECRET_KEY = 'your_minio_secret_key'
MINIO_BUCKET_NAME = 'your_minio_bucket_name'

# AES encryption parameters
AES_KEY_SIZE = 32  # AES-256
SALT_SIZE = 16
ITERATIONS = 100000

def encrypt_data(data: io.BytesIO, password: str):
    # Generate a random salt
    salt = get_random_bytes(SALT_SIZE)

    # Derive a key from the password using PBKDF2
    key = PBKDF2(password.encode('utf-8'), salt, dkLen=AES_KEY_SIZE, count=ITERATIONS)

    # Initialize the AES cipher in CBC mode with the derived key and a random IV
    cipher = AES.new(key, AES.MODE_CBC)

    # Create an in-memory buffer to store the encrypted data
    encrypted_data = io.BytesIO()

    # Write the salt and IV to the buffer
    encrypted_data.write(salt)
    encrypted_data.write(cipher.iv)

    # Encrypt the data and write it to the buffer
    while True:
        chunk = data.read(8192)
        if not chunk:
            break
        elif len(chunk) % AES.block_size != 0:
            # Pad the chunk to a multiple of the AES block size
            chunk = pad(chunk, AES.block_size)
        encrypted_data.write(cipher.encrypt(chunk))

    # Set the buffer to the beginning
    encrypted_data.seek(0)

    return encrypted_data

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), password: str = None):
    # Check if the file is provided as io.BytesIO
    if isinstance(file, io.BytesIO):
        # Encrypt the data
        encrypted_data = encrypt_data(file, password)

        # Upload the encrypted data to MinIO
        minio_client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
        minio_client.put_object(MINIO_BUCKET_NAME, file.filename, encrypted_data, len(encrypted_data.getvalue()))

        # Close the buffer
        encrypted_data.close()
    else:
        # Encrypt the file data
        encrypted_data = encrypt_data(io.BytesIO(await file.read()), password)

        # Upload the encrypted data to MinIO
        minio_client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
        minio_client.put_object(MINIO_BUCKET_NAME, file.filename, encrypted_data, len(encrypted_data.getvalue()))

        # Close the buffer
        encrypted_data.close()

    return {"message": "File uploaded successfully."}

@app.get("/download/{file_name}")
async def download_file(file_name: str, password: str = None):
    # Download the file from MinIO
    minio_client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
    file_data = minio_client.get_object(MINIO_BUCKET_NAME, file_name).read()

    # Check if password is provided for decryption
    if password:
        # Read the salt and IV from the encrypted data
        salt = file_data[:SALT_SIZE]
        iv = file_data[SALT_SIZE:SALT_SIZE + AES.block_size]

        # Derive the key from the password and salt using PBKDF2
        key = PBKDF2(password.encode('utf-8'), salt, dkLen=AES_KEY_SIZE, count=ITERATIONS)

        # Initialize the AES cipher in CBC mode with the derived key and IV
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)

        # Decrypt the data
        file_data = unpad(cipher.decrypt(file_data[SALT_SIZE + AES.block_size:]), AES.block_size)

    # Return the file data as a file response
    return StreamingResponse(io.BytesIO(file_data), media_type='application/octet-stream', headers={'Content-Disposition': f'attachment; filename="{file_name}"'})
