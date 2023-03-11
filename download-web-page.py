import requests

url = 'https://sift.com/developers/docs/curl/apis-overview'
r = requests.get(url, allow_redirects=True)

open('api-reference.html', 'wb').write(r.content)
