import requests
import json
import time
import hashlib
import random
import sys


# Generate table Randomly
alphabet = list('abcdefghijklmnopqrstuvwxyz')
random.shuffle(alphabet)
table = ''.join(alphabet)[:10]


def MD5(s):
    return hashlib.md5(s.encode()).hexdigest()


def encrypt(s):
    result = ''
    for i in s:
        result += table[ord(i) - ord('0')]
    # print(result)
    return result


def Run(IEMI=None):
    if IEMI is None:
        # Input to IMEI
        if(len(sys.argv) > 1):
            IMEI = sys.argv[1]
        else:
            IMEI = str(input("Please Input Your IMEI Arg:"))
        if(len(IMEI) != 32):
            exit("IMEI Format Error!")

        if (len(sys.argv) > 2 and sys.argv[2].upper() == 'Y'):
            pass
        else:
            print("Your IEME Code:", IMEI)
            Sure = str(input("Sure?(Y/N)"))
            if(Sure == 'Y' or Sure == 'y'):
                pass
            else:
                exit("User Aborted.")

    API_ROOT = 'http://client3.aipao.me/api'  # client3 for Android
    Version = '2.14'

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

    # Get User Info

    GSurl = API_ROOT + '/' + token + '/QM_Users/GS'
    GSres = requests.get(GSurl, headers=header, data={})
    GSjson = json.loads(GSres.content.decode('utf8', 'ignore'))

    Lengths = GSjson['Data']['SchoolRun']['Lengths']

    print(Lengths)
    # Start Running
    SRSurl = API_ROOT + '/' + token + \
        '/QM_Runs/SRS?S1=30.534736&S2=114.367788&S3=' + str(Lengths)
    SRSres = requests.get(SRSurl, headers=header, data={})
    SRSjson = json.loads(SRSres.content.decode('utf8', 'ignore'))

    # Generate Runnig Data Randomly
    RunTime = str(random.randint(720, 1000))  # seconds
    RunDist = str(Lengths + random.randint(0, 3))  # meters
    RunStep = str(random.randint(1300, 1600))  # steps

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


def main():
    Run()


if __name__ == '__main__':
    main()
