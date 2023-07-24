from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad
from minio import Minio
import tempfile
import os

# MinIO configuration
MINIO_ENDPOINT = 'your_minio_endpoint'
MINIO_ACCESS_KEY = 'your_minio_access_key'
MINIO_SECRET_KEY = 'your_minio_secret_key'
MINIO_BUCKET_NAME = 'your_minio_bucket_name'
ENCRYPTED_FILE_NAME = 'encrypted_file.bin'
DECRYPTED_FILE_NAME = 'decrypted_file.txt'

# AES encryption parameters
AES_KEY_SIZE = 32  # AES-256
SALT_SIZE = 16
ITERATIONS = 100000

def encrypt_file(input_file, password):
    # Generate a random salt
    salt = os.urandom(SALT_SIZE)

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
    with open(input_file, 'rb') as file_in:
        while True:
            chunk = file_in.read(8192)
            if not chunk:
                break
            elif len(chunk) % AES.block_size != 0:
                # Pad the chunk to a multiple of the AES block size
                chunk = pad(chunk, AES.block_size)
            temp_file.write(cipher.encrypt(chunk))

    # Close the temporary file
    temp_file.close()

    return temp_file.name

def decrypt_file(input_file, password):
    # Create a temporary file to store the decrypted data
    temp_file = tempfile.NamedTemporaryFile(delete=False)

    # Open the input file
    with open(input_file, 'rb') as file_in:
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
            temp_file.write(decrypted_chunk)

    # Close the temporary file
    temp_file.close()

    return temp_file.name

def upload_to_minio(file_path, object_name):
    minio_client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)

    try:
        minio_client.fput_object(MINIO_BUCKET_NAME, object_name, file_path)
        print(f"File uploaded to MinIO with object name: {object_name}")
    except Exception as e:
        print(f"Error uploading file to MinIO: {e}")

def download_from_minio(object_name):
    minio_client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)

    try:
        # Create a temporary file to store the downloaded data
        temp_file = tempfile.NamedTemporaryFile(delete=False)

        # Download the object from MinIO and write it to the temporary file
        minio_client.fget_object(MINIO_BUCKET_NAME, object_name, temp_file.name)

        # Close the temporary file
        temp_file.close()

        return temp_file.name
    except Exception as e:
        print(f"Error downloading file from MinIO: {e}")

if __name__ == "__main__":
    input_file_path = 'path_to_your_input_file.txt'
    password = 'your_password_here'

    # Encrypt the file and get the path of the temporary encrypted file
    encrypted_file_path = encrypt_file(input_file_path, password)

    # Upload the encrypted file to MinIO
    upload_to_minio(encrypted_file_path, ENCRYPTED_FILE_NAME)

    # Download the encrypted file from MinIO and get the path of the temporary downloaded file
    downloaded_file_path = download_from_minio(ENCRYPTED_FILE_NAME)

    # Decrypt the file and get the path of the temporary decrypted file
    decrypted_file_path = decrypt_file(downloaded_file_path, password)

    # Do something with the decrypted file

    # Delete the temporary files
    os.remove(encrypted_file_path)
    os.remove(downloaded_file_path)
    os.remove(decrypted_file_path)
