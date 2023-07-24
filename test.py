from fastapi import FastAPI, UploadFile, File
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad
from minio import Minio
import tempfile
import os

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

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), password: str = None):
    # Generate a random salt
    salt = get_random_bytes(SALT_SIZE)

    # Derive a key from the password using PBKDF2
    key = PBKDF2(password, salt, dkLen=AES_KEY_SIZE, count=ITERATIONS)

    # Initialize the AES cipher in CBC mode with the derived key and a random IV
    cipher = AES.new(key, AES.MODE_CBC)

    # Create a temporary file to store the encrypted data
    temp_file = tempfile.NamedTemporaryFile(delete=False)

    # Write the salt and IV to the temporary file
    temp_file.write(salt)
    temp_file.write(cipher.iv)

    # Encrypt the file and write it to the temporary file
    while True:
        chunk = await file.read(8192)
        if not chunk:
            break
        elif len(chunk) % AES.block_size != 0:
            # Pad the chunk to a multiple of the AES block size
            chunk = pad(chunk, AES.block_size)
        temp_file.write(cipher.encrypt(chunk))

    # Close the temporary file
    temp_file.close()

    # Upload the encrypted file to MinIO
    minio_client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
    with open(temp_file.name, 'rb') as file_data:
        minio_client.put_object(MINIO_BUCKET_NAME, file.filename, file_data)

    # Delete the temporary file
    os.remove(temp_file.name)

    return {"message": "File uploaded successfully."}
@app.get("/download/{file_name}")
async def download_file(file_name: str, password: str = None):
    # Download the encrypted file from MinIO
    minio_client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    with open(temp_file.name, 'wb') as file_data:
        file_data.write(minio_client.get_object(MINIO_BUCKET_NAME, file_name).read())

    # Create a temporary file to store the decrypted data
    decrypted_temp_file = tempfile.NamedTemporaryFile(delete=False)

    # Open the input file (encrypted data)
    with open(temp_file.name, 'rb') as file_in:
        # Read the salt and IV from the input file
        salt = file_in.read(SALT_SIZE)
        iv = file_in.read(AES.block_size)

        # Derive the key from the password and salt using PBKDF2
        key = PBKDF2(password, salt, dkLen=AES_KEY_SIZE, count=ITERATIONS)

        # Initialize the AES cipher in CBC mode with the derived key and IV
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)

        # Decrypt the file and write it to the temporary file
        while True:
            chunk = file_in.read(8192)
            if not chunk:
                break
            decrypted_chunk = cipher.decrypt(chunk)
            if len(decrypted_chunk) < len(chunk):
                # Unpad the decrypted chunk if necessary
                decrypted_chunk = unpad(decrypted_chunk, AES.block_size)
            decrypted_temp_file.write(decrypted_chunk)

    # Close the temporary files
    temp_file.close()
    decrypted_temp_file.close()

    # Delete the encrypted temporary file
    os.remove(temp_file.name)

    return FileResponse(decrypted_temp_file.name, media_type='application/octet-stream', headers={'Content-Disposition': f'attachment; filename="{file_name}"'})
