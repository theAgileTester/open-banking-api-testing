import requests

url = "https://auth.truelayer-sandbox.com/connect/token"

payload = 'grant_type=authorization_code&client_id=sandbox-obsandboxtesting-a42772&client_secret=tlcs_sandbox_nn8bm5kfjp53_dCBPcbsu5zFSRhIhBYMPdLtu9k90tRLxrU5S7eG0IisE&redirect_uri=https%3A%2F%2Fconsole.truelayer.com%2Fredirect-page&code=EAD96A772681B6B643E0EEE9429D794F5E6EB248EA0BB41D92531E2FA5E5D9A9'
headers = {
  'Content-Type': 'application/x-www-form-urlencoded'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
