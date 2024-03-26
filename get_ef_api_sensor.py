# Example Code to obtain data from API for specific sensors on an EcoFlow device
# Mark Hicks - 01/29/2024

import hashlib
import hmac
import json
import random
import requests
import time
from urllib.parse import urlencode

def hmac_sha256(data, key):
  hashed = hmac.new(key.encode('utf-8'), data.encode('utf-8'), hashlib.sha256).digest()
  return ''.join(format(byte, '02x') for byte in hashed)

def get_map(json_obj, prefix=""):
  def flatten(obj, pre=""):
    result = {}
    if isinstance(obj, dict):
      for k, v in obj.items():
        result.update(flatten(v, f"{pre}.{k}" if pre else k))
    elif isinstance(obj, list):
      for i, item in enumerate(obj):
        result.update(flatten(item, f"{pre}[{i}]"))
    else: result[pre] = obj
    return result
  return flatten(json_obj, prefix)

def get_qstr(params): return '&'.join([f"{key}={params[key]}" for key in sorted(params.keys())])

def post_api(url, key, secret, params=None):
  nonce     = str(random.randint(100000, 999999))
  timestamp = str(int(time.time() * 1000))
  headers   = {'accessKey':key,'nonce':nonce,'timestamp':timestamp}
  sign_str  = (get_qstr(get_map(params)) + '&' if params else '') + get_qstr(headers)
  headers['sign'] = hmac_sha256(sign_str, secret)
  response = requests.post(url, headers=headers, json=params)
  if response.status_code == 200: return response.json()
  else: print(f"get_api: {response.text}")
 
if __name__ == "__main__":

  url     = 'https://api.ecoflow.com/iot-open/sign/device/quota'
  quotas  = ["inv.cfgAcEnabled","inv.cfgAcXboost"]
  params  = {"cmdSet":32,"id":66,"quotas":quotas}

  # Replace with valid access/secret keys and device SN
  key     = 'Fp4SvIprYSDPXtYJidEtUAd1o'
  secret  = 'WIbFEKre0s6sLnh4ei7SPUeYnptHG6V'
  sn      = 'DCABZ0123456789'

  payload = post_api(url,key,secret,{"sn":sn,"params":params})
  print(json.dumps(payload,indent=2))
