from Cryptodome.PublicKey import RSA

# Tạo cặp khóa
key = RSA.generate(1024)

# Lấy khóa riêng
private_key = key.export_key()

# Lấy khóa công khai
public_key = key.publickey().export_key()

# In khóa riêng và khóa công khai
print("Khóa riêng (Private key):")
print(private_key.decode())

print("\nKhóa công khai (Public key):")
print(public_key.decode())




----
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import unpad
from minio import Minio

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

def decrypt_file(input_file, output_file, password):
    # Open the input and output files
    with open(input_file, 'rb') as file_in, open(output_file, 'wb') as file_out:
        # Read the salt and IV from the input file
        salt = file_in.read(SALT_SIZE)
        iv = file_in.read(AES.block_size)

        # Derive the key from the password and salt using PBKDF2
        key = PBKDF2(password, salt, dkLen=AES_KEY_SIZE, count=ITERATIONS)

        # Initialize the AES cipher in CBC mode with the derived key and IV
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)

        # Decrypt the file and write it to the output file
        while True:
            chunk = file_in.read(8192)
            if len(chunk) == 0:
                break
            decrypted_chunk = cipher.decrypt(chunk)
            if len(decrypted_chunk) < len(chunk):
                # Unpad the decrypted chunk if necessary
                decrypted_chunk = unpad(decrypted_chunk, AES.block_size)
            file_out.write(decrypted_chunk)

def download_from_minio(object_name, file_path):
    minio_client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)

    try:
        minio_client.fget_object(MINIO_BUCKET_NAME, object_name, file_path)
        print(f"File downloaded from MinIO with object name: {object_name}")
    except Exception as e:
        print(f"Error downloading file from MinIO: {e}")

if __name__ == "__main__":
    password = 'your_password_here'

    encrypted_file_path = 'encrypted_file.bin'
    download_from_minio(ENCRYPTED_FILE_NAME, encrypted_file_path)

    decrypted_file_path = 'decrypted_file.txt'
    decrypt_file(encrypted_file_path, decrypted_file_path, password)


