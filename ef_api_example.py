'''
Example Code to obtain data via API from SHP, DP, D2, D2M
for all or specific sensors and modify specific settings

Mark Hicks - 03/11/2024
'''
### INPUT YOUR API KEYS AND DEVICE SERIAL NUMBERS AT THE BOTTOM OF THIS SCRIPT ###

import hashlib
import hmac
import json
import random
import requests
import time
from urllib.parse import urlencode

def banner(message, fg="BLACK", bg="YELLOW"):
    spacing = "─" * len(message)
    print(f"┌─{spacing}─┐")
    print(f"│ {message} │")
    print(f"└─{spacing}─┘")
    print()

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

def ef_api(method, url, key, secret, params=None):
  if method == 'GET': url += '?' + urlencode(params)
  nonce     = str(random.randint(100000, 999999))
  timestamp = str(int(time.time() * 1000))
  headers   = {'accessKey':key,'nonce':nonce,'timestamp':timestamp}
  sign_str  = (get_qstr(get_map(params)) + '&' if params else '') + get_qstr(headers)
  headers['sign'] = hmac_sha256(sign_str, secret)
  response = requests.request(method, url, headers=headers, json=params if method != 'GET' else None)
  print(f"{method}: {url}")
  print("Signed:", sign_str)
  if response.status_code == 200:
    return response.json()
  else:
    print("Response: ", response.text)

def demo_api(url, key, secret, devices):

  for device in devices:

    name    = device['name']
    sn      = device['sn']
    quotas  = device['quotas']
    setting = device['setting']
    mod     = device['mod']
    op      = device['op']
    params  = device['params']

    banner(f'Get All Quotas for {name}')
    payload = ef_api('GET',f"{url}/all",key,secret,{'sn':sn})
    print("Data:", payload['data'])
    print()
    
    banner(f'Get Specific Quotas for {name}')
    print()
    payload = ef_api('POST',url,key,secret,{"sn":sn,"params":{"quotas":quotas}})
    print(json.dumps(payload['data'],indent=2))
    print()

    banner(f'Modify {setting} for {name}')
    print()
    for p in params:
      payload = ef_api('PUT',url,key,secret,{"sn":sn,"moduleType":mod,"operateType":op,"params":p})
      print("Message:", payload['message'])
      time.sleep(2)
      print()

if __name__ == "__main__":

  url     = 'https://api.ecoflow.com/iot-open/sign/device/quota'
  key     = 'Fp4SvIprYSDPXtYJidEtUAd1o'
  secret  = 'WIbFEKre0s6sLnh4ei7SPUeYnptHG6V'
  
  devices = [

    {'name'   : 'Smart Home Panel',
     'sn'     : 'SP10Z12345678901',
     'quotas' : ["epsModeInfo.eps","backupChaDiscCfg.forceChargeHigh","backupChaDiscCfg.discLower"],
     'setting': 'EPS Mode','mod':'','op':'',
     'params' : [{"cmdSet":11,"id":24,"eps":1},{"cmdSet":11,"id":24,"eps":0}]
    },

    {'name'   : 'Delta Pro',
     'sn'     : 'DCABZ0123456789' ,
     'quotas' : ["pd.beepState","mppt.carState","inv.cfgAcEnabled","inv.cfgAcXboost"],
     'setting': 'Silent Mode','mod':'','op':'',
     'params' : [{"cmdSet":32,"id":38,"enabled":1},{"cmdSet":32,"id":38,"enabled":0}]
    },

    {'name'   : 'Delta 2',
     'sn'     : 'R331Z12345678901',
     'quotas' : ["pd.beepMode","pd.dcOutState","inv.cfgAcEnabled","inv.cfgAcXboost"],
     'setting': 'Silent Mode','mod':5,'op':'quietMode',
     'params' : [{"enabled":1},{"enabled":0}]
    },

    {'name'   : 'Delta 2 Max',
     'sn'     : 'R351Z12345678901',
     'quotas' : ["pd.beepMode","pd.dcOutState","inv.cfgAcEnabled","inv.cfgAcXboost"],
     'setting': 'Silent Mode','mod':1,'op':'quietCfg',
     'params' : [{"enabled":1},{"enabled":0}]
    }
  ]

demo_api(url, key, secret, devices)
