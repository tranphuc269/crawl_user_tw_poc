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
