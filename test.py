from fastapi import FastAPI, UploadFile, File
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad
from minio import Minio
import io

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

    # Create an in-memory buffer to store the encrypted data
    encrypted_data = io.BytesIO()

    # Write the salt and IV to the buffer
    encrypted_data.write(salt)
    encrypted_data.write(cipher.iv)

    # Encrypt the file and write it to the buffer
    while True:
        chunk = await file.read(8192)
        if not chunk:
            break
        elif len(chunk) % AES.block_size != 0:
            # Pad the chunk to a multiple of the AES block size
            chunk = pad(chunk, AES.block_size)
        encrypted_data.write(cipher.encrypt(chunk))

    # Upload the encrypted data to MinIO
    minio_client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
    encrypted_data.seek(0)
    minio_client.put_object(MINIO_BUCKET_NAME, file.filename, encrypted_data, len(encrypted_data.getvalue()))

    # Close the buffer
    encrypted_data.close()

    return {"message": "File uploaded successfully."}
from fastapi import FastAPI
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import unpad
from minio import Minio

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

@app.get("/download/{file_name}")
async def download_file(file_name: str, password: str = None):
    # Download the encrypted file from MinIO
    minio_client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
    encrypted_data = minio_client.get_object(MINIO_BUCKET_NAME, file_name).read()

    # Read the salt and IV from the encrypted data
    salt = encrypted_data[:SALT_SIZE]
    iv = encrypted_data[SALT_SIZE:SALT_SIZE + AES.block_size]

    # Derive the key from the password and salt using PBKDF2
    key = PBKDF2(password, salt, dkLen=AES_KEY_SIZE, count=ITERATIONS)

    # Initialize the AES cipher in CBC mode with the derived key and IV
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)

    # Decrypt the data
    decrypted_data = cipher.decrypt(encrypted_data[SALT_SIZE + AES.block_size:])

    # Unpad the decrypted data
    decrypted_data = unpad(decrypted_data, AES.block_size)

    # Return the decrypted data as a file response
    return StreamingResponse(io.BytesIO(decrypted_data), media_type='application/octet-stream', headers={'Content-Disposition': f'attachment; filename="{file_name}"'})
