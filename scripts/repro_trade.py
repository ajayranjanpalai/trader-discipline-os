import json, urllib.request, urllib.error, time
base='http://127.0.0.1:5000'
email=f'testuser{int(time.time())}@example.com'
# Signup
data={'name':'Test User','email':email,'password':'password123'}
req=urllib.request.Request(base+'/api/auth/signup', data=json.dumps(data).encode(), headers={'Content-Type':'application/json'})
try:
    resp=urllib.request.urlopen(req)
    body=json.loads(resp.read())
    token=body['token']
    print('Signed up, token length', len(token))
except urllib.error.HTTPError as e:
    print('Signup failed', e.code, e.read())
    raise
# Post trade
trade={'pair':'BTCUSD','direction':'long','entry':30000,'exit':31000,'stop_loss':29500,'position_size':1,'pnl':1000,'risk_reward':3.0,'emotion':'neutral','timestamp':None}
req=urllib.request.Request(base+'/api/trades', data=json.dumps(trade).encode(), headers={'Content-Type':'application/json','Authorization':'Bearer '+token})
try:
    resp=urllib.request.urlopen(req)
    print('Trade response', resp.status, resp.read())
except urllib.error.HTTPError as e:
    print('Trade failed', e.code)
    print(e.read())
    raise
