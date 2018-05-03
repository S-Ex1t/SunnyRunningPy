import requests
import json
import time
import hashlib
import random
import sys


def MD5(s):
    return hashlib.md5(s.encode()).hexdigest()


def encrypt(s):
    result = ''
    for i in s:
        result += table[ord(i) - ord('0')]
    # print(result)
    return result


# Input to IMEI
if(len(sys.argv) > 1):
    IMEI = sys.argv[1]
else:
    IMEI = str(input("Please Input Your IMEI Arg:"))
if(len(IMEI) != 32):
    exit("IMEI Format Error!")


print("Your IEME Code:", IMEI)
Sure = str(input("Sure?(Y/N)"))
if(Sure == 'Y' or Sure == 'y'):
    pass
else:
    exit("User Aborted.")


# Generate table Randomly
alphabet = list('abcdefghijklmnopqrstuvwxyz')
random.shuffle(alphabet)
table = ''.join(alphabet)[:10]

API_ROOT = 'http://client3.aipao.me/api'
Version = '2.14'

# Generate Runnig Data Randomly
RunTime = str(random.randint(720, 1000))  # seconds
RunDist = str(2000 + random.randint(0, 3))  # meters
RunStep = str(random.randint(1300, 1600))  # steps

# Login
TokenRes = requests.get(
    API_ROOT + '/%7Btoken%7D/QM_Users/Login_AndroidSchool?IMEICode=' + IMEI)
TokenJson = json.loads(TokenRes.content.decode('utf8', 'ignore'))

# headers
token = TokenJson['Data']['Token']
userId = str(TokenJson['Data']['UserId'])
timespan = str(time.time()).replace('.', '')[:13]
auth = 'B' + MD5(MD5(IMEI)) + ':;' + token
nonce = str(random.randint(100000, 10000000))
sign = MD5(token + nonce + timespan + userId).upper()  # sign为大写


header = {'nonce': nonce, 'timespan': timespan,
          'sign': sign, 'version': Version, 'Accept': None, 'User-Agent': None, 'Accept-Encoding': None, 'Connection': 'Keep-Alive'}

# Start Running
SRSurl = API_ROOT + '/' + token + '/QM_Runs/SRS?S1=30.534738&S2=114.367788&S3=2000'
SRSres = requests.get(SRSurl, headers=header, data={})
SRSjson = json.loads(SRSres.content.decode('utf8', 'ignore'))


# Running Sleep
StartT = time.time()
for i in range(int(RunTime)):
    time.sleep(1)
    print("Current Minutes: %d Running Progress: %.2f%%\r" %
          (i / 60, i * 100.0 / int(RunTime)), end='')
print("")
print("Running Seconds:", time.time() - StartT)


# print(SRSurl)
# print(SRSjson)

RunId = SRSjson['Data']['RunId']

# End Running
EndUrl = API_ROOT + '/' + token + '/QM_Runs/ES?S1=' + RunId + '&S4=' + \
    encrypt(RunTime) + '&S5=' + encrypt(RunDist) + \
    '&S6=&S7=1&S8=' + table + '&S9=' + encrypt(RunStep)

EndRes = requests.get(EndUrl, headers=header)
EndJson = json.loads(EndRes.content.decode('utf8', 'ignore'))

print("-----------------------")
print("Time:", RunTime)
print("Distance:", RunDist)
print("Steps:", RunStep)
print("-----------------------")

if(EndJson['Success']):
    print("[+]OK:", EndJson['Data'])
else:
    print("[!]Fail:", EndJson['Data'])
