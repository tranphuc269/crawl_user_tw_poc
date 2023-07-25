import base64

def base64_decode_with_padding(base64_string):
    # Kiểm tra xem chuỗi base64 có độ dài chia hết cho 4 hay không
    padding_needed = len(base64_string) % 4
    if padding_needed > 0:
        base64_string += "=" * (4 - padding_needed)

    # Giải mã chuỗi base64 thành dữ liệu ban đầu
    try:
        decoded_data = base64.b64decode(base64_string)
        return decoded_data
    except Exception as e:
        print("Error decoding base64:", e)
        return None

# Chuỗi base64 cần giải mã
base64_string = "SGVsbG8gV29ybGQh"

# Giải mã base64 với xử lý padding
decoded_data = base64_decode_with_padding(base64_string)

# Chuyển đổi dữ liệu giải mã thành chuỗi (nếu là dữ liệu văn bản)
if decoded_data:
    decoded_text = decoded_data.decode('utf-8')
    print(decoded_text)  # Kết quả: "Hello World!"
else:
    print("Invalid base64 string.")
