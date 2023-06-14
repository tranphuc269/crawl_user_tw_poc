import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


curl_command = '''
curl --location 'https://twitter.com/i/api/1.1/search/typeahead.json?include_ext_is_blue_verified=1&include_ext_verified_type=1&include_ext_profile_image_shape=1&q=phuc&src=search_box&result_type=events%2Cusers%2Ctopics' \
--header 'Authorization: Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA' \
--header 'Cookie: guest_id=v1%3A167176499478279878; _ga=GA1.2.1579385385.1672718365; guest_id_marketing=v1%3A167176499478279878; guest_id_ads=v1%3A167176499478279878; g_state={"i_l":0}; kdt=enc1yMa6OiY8wzDb6eBhXUBG5gQdV4gPU5Pirhrn; auth_token=9ba194ed89e09f8d29117584ffc4335e5f7536f0; ct0=eb9f4fc6f9e062bb6b30d5d81cd3764a568823b099882d25293e1dc643f53dec582bdbe99a076b9040752f6bf04794ad0c6184993a3b84d381b5689ee932b41c19c752f66eb9998b60816964b8f13b81; twid=u%3D1456283845561487361; lang=en; _gid=GA1.2.1463282300.1686732168; personalization_id="v1_ZZv4YjTad2TkcqtPk3AeKA=="; ct0=3b86c864150828855b3f5b983103a3bf366edafd9d70bd5e21fa866fca8aa85c30414114fee631e2ad3cce6cc24669326959cfcde036a7663258695487656d38f29e70b2c5a9f1ff3c161bfa0686e0e6; guest_id=v1%3A168673323957335130; guest_id_ads=v1%3A168673323957335130; guest_id_marketing=v1%3A168673323957335130; personalization_id="v1_y8+HmZ5a2vLX5tYLbwJzhw=="; ct0=3b86c864150828855b3f5b983103a3bf366edafd9d70bd5e21fa866fca8aa85c30414114fee631e2ad3cce6cc24669326959cfcde036a7663258695487656d38f29e70b2c5a9f1ff3c161bfa0686e0e6; guest_id=v1%3A168673323957335130; guest_id_ads=v1%3A168673323957335130; guest_id_marketing=v1%3A168673323957335130; personalization_id="v1_y8+HmZ5a2vLX5tYLbwJzhw=="' \
--header 'X-Csrf-Token: eb9f4fc6f9e062bb6b30d5d81cd3764a568823b099882d25293e1dc643f53dec582bdbe99a076b9040752f6bf04794ad0c6184993a3b84d381b5689ee932b41c19c752f66eb9998b60816964b8f13b81'
'''
duration = 10  # second
num_threads = 4  #

def execute_curl():
    process = subprocess.Popen(curl_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    if process.returncode == 0:
        return "Success"
    elif process.returncode == 403:
        return "API blocked"
    else:
        return "Something wrong!"

start_time = time.time()

with ThreadPoolExecutor(max_workers=num_threads) as executor:
    futures = []
    while (time.time() - start_time) < duration:
        futures.append(executor.submit(execute_curl))
        time.sleep(1)

    for future in as_completed(futures):
        result = future.result()
        print(result)