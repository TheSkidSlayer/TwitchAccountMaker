import os
import sys
import time
import string
import random
from threading import Thread
from requests_futures.sessions import FuturesSession

if sys.platform == "linux":
    clear = lambda: os.system("clear")
else:
    clear = lambda: os.system("cls")

num = 0
proxies = []
session = FuturesSession()
capmonster_api_key = "Api key here"

class Email:

    def Get_Code(email):
        r = session.get(f"http://foreskin.market/api/latest/{email}?no-reply@twitch.tv").result()
        if "verify_code" in r.text:
            code = r.text.split('vertical-align:top;word-wrap:break-word;border-radius:2px;overflow:hidden"><a href="')[1].split("\"")[0]
            return code
        else:
            return False

    def Create(email):
        session.get(f'http://foreskin.market/api/{email}@foreskin.market')
        return f"{email}@foreskin.market"

class Capmonster:
    
    def Get_Balance():
        try:
            json = {
                "clientKey": capmonster_api_key
            }
            r = session.post('https://api.capmonster.cloud/getBalance', json=json).result()
            if r.json()['errorId'] == 1:
                return 'error, information about it is in the errorCode property'
            if r.json()['errorId'] == 0:
                return r.json()['balance']
        except:
            pass

    def Create_Task():
        try:
            json = {
                "clientKey": capmonster_api_key,
                "task": {
                    "type": 'FunCaptchaTaskProxyless',
                    "websiteURL": "https://nojs-game3-prod-ap-southeast-1.arkoselabs.com/fc/api/nojs/?pkey=E5554D43-23CC-1982-971D-6A2262A2CA24",
                    "websitePublicKey": "E5554D43-23CC-1982-971D-6A2262A2CA24",
                    "minScore": 0.3
                }
            }
            r = session.post('https://api.capmonster.cloud/createTask', json=json).result()
            if r.json()['errorId'] == 1:
                return 'error, information about it is in the errorCode property'
            if r.json()['errorId'] == 0:
                return r.json()['taskId']
        except:
            pass

    def Get_Task_Result(task_id):
        try:
            json = {
                "clientKey": capmonster_api_key,
                "taskId": task_id
            }
            r = session.post('https://api.capmonster.cloud/getTaskResult', json=json).result()
            if r.json()['errorId'] == 1:
                return 'error, information about it is in the errorCode property'
            if r.json()['errorId'] == 0:
                if r.json()['status'] == 'processing':
                    return 'processing'
                if r.json()['status'] == 'ready':
                    return r.json()['solution']['token']
        except:
            pass

class Twitch:

    def Save(name, data):
        with open(f"{name}.txt", "a+") as f:
            f.write(f"{data}\n")
            f.close()

    def Send_Code(token):
        headers = {
            "Authorization": f"OAuth {token}"
        }
        json = [{"operationName":"CoreAuthCurrentUser","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"bc444c5b28754cb660ed183236bb5fe083f2549d1804a304842dad846d51f3ee"}}},{"operationName":"VerficationCodeUser","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"77d945a4cee34ec9008cc61a978d7baeabce0631f2aa0076977ba13ac409dda2"}}}]
        session.post("https://gql.twitch.tv/gql", json=json, headers=headers).result()

    def Verify(token, opaqueID):
        headers = {
            "Authorization": f"OAuth {token}",
            "Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko"
        }
        json = [{"operationName":"VerifyEmail","variables":{"input":{"opaqueID":opaqueID}},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"4d3cbb19003b87567cb6f59b186e989c69b0751ecdd799be6004d200014258f1"}}}]
        r = session.post("https://gql.twitch.tv/gql", json=json, headers=headers).result()
        if r.json()[0]["data"]["verifyContactMethod"]["isSuccess"]:
            return True
        else:
            return False

    def Create(captcha):
        global num
        try:
            proxy = random.choice(proxies)
            username = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(6))
            email = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(12))
            email = Email.Create(email)
            password = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(15))
            json = {"username":username,"password":password,"email":f"{email}","birthday":{"day":15,"month":2,"year":2000},"client_id":"kimne78kx3ncx6brgo4mv6wki5h1ko","include_verification_code":True,"arkose":{"token":captcha}}
            r = session.post("https://passport.twitch.tv/register", json=json, proxies={"https": f"http://{proxy}"}, timeout=4).result()
            if "access_token" in r.text:
                token = r.json()["access_token"]
                Twitch.Send_Code(token)
                while True:
                    verify_code = Email.Get_Code(email)
                    if verify_code == False:
                        continue
                    else:
                        break
                opaqueID = verify_code.split("email-verification/")[1].split("?")[0]
                if Twitch.Verify(token, opaqueID):
                    num += 1
                    print(f"[\x1b[38;5;199m$\x1b[0m] Successfully Created Verified Account \x1b[38;5;199m#\x1b[0m{num} [\x1b[38;5;199m{username}:{password}\x1b[0m]")
                    Twitch.Save("Accounts", f"{username}:{password}:{token}")
                    Twitch.Save("Tokens", f"{token}")
        except:
            try:
                proxies.remove(proxy)
            except:
                pass
            Twitch.Create(captcha)

def Load_Proxy():
    for line in open('Proxies.txt'):
        proxies.append(line.replace('\n', ''))
    print(f"[\x1b[38;5;199m$\x1b[0m] Loaded {len(proxies)} Proxies")

def Task():
    tid = Capmonster.Create_Task()
    while True:
        captcha = Capmonster.Get_Task_Result(tid)
        if captcha == 'processing':
            pass
        else:
            break
    try:
        if "error" in captcha:
            Task()
    except:
        print("[\x1b[38;5;199m$\x1b[0m] Fatal Captcha Error.")
    else:
        Twitch.Create(captcha)

if __name__ == "__main__":
    clear()
    print("""
\x1b[38;5;199m.▄▄ · ▄▄▌ ▐ ▄▌ ▄▄▄· ▄▄▄▄▄▄▄▄▄▄▄▄▄ .·▄▄▄▄  
▐█ ▀. ██· █▌▐█▐█ ▀█ •██  •██  ▀▄.▀·██▪ ██ 
▄▀▀▀█▄██▪▐█▐▐▌▄█▀▀█  ▐█.▪ ▐█.▪▐▀▀▪▄▐█· ▐█▌
▐█▄▪▐█▐█▌██▐█▌▐█ ▪▐▌ ▐█▌· ▐█▌·▐█▄▄▌██. ██ 
 ▀▀▀▀  ▀▀▀▀ ▀▪ ▀  ▀  ▀▀▀  ▀▀▀  ▀▀▀ ▀▀▀▀▀• \x1b[0mTwitch
""")
    Load_Proxy()
    print(f"[\x1b[38;5;199m$\x1b[0m] Current Balance: {Capmonster.Get_Balance()}")
    print()
    while True:
        Thread(target=Task).start()
        time.sleep(5)
