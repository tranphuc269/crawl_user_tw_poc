import concurrent.futures
import requests

# Danh sách các URL bạn muốn yêu cầu
urls = ["https://example.com/page1", "https://example.com/page2", "https://example.com/page3"]

def fetch_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return f"Yêu cầu thành công cho URL: {url}"
    else:
        return f"Yêu cầu thất bại cho URL: {url}"

# Sử dụng ThreadPoolExecutor để thực hiện các yêu cầu song song
with concurrent.futures.ThreadPoolExecutor() as executor:
    results = list(executor.map(fetch_url, urls))

# In kết quả
for result in results:
    print(result)
