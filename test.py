from Crypto.Cipher import AES
import binascii

# Hàm giải mã AES CBC PKCS5 Padding
def aes_decrypt(ciphertext, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext)
    return plaintext.rstrip(b"\0")

# Dữ liệu HEX String mã hóa
encrypted_data_hex = "your_hex_string_here"

# Key và initialization vector (iv) đã cho trước (dưới dạng HEX String)
key_hex = "your_key_hex_string_here"
iv_hex = "your_iv_hex_string_here"

# Chuyển đổi dữ liệu HEX String sang dạng bytes
ciphertext = binascii.unhexlify(encrypted_data_hex)

# Chuyển đổi key và iv từ dạng HEX String sang dạng bytes
key = binascii.unhexlify(key_hex)
iv = binascii.unhexlify(iv_hex)

# Giải mã dữ liệu
plaintext = aes_decrypt(ciphertext, key, iv)

# Hiển thị dữ liệu giải mã dưới dạng chuỗi
plaintext_str = plaintext.decode("utf-8")
print("Decrypted data:", plaintext_str)
