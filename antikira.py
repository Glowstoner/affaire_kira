#!/bin/python3

import instaloader
import requests
import time
import sys
import os
import re

def import_proxies():
    f = open("proxies.txt", "r")
    proxy_list = []
    proxy_list.append(None)
    for lines in f.readlines():
        proxyDict = {
                "http":  "http://"+lines, 
                "https": "https://"+lines,
                "ftp":   "ftp://"+lines
        }
        
        proxy_list.append(proxyDict)

    return proxy_list

def relations(account):
    user = "raoulgrimard"
    loader = instaloader.Instaloader()

    try:
        loader.load_session_from_file(user)
    except FileNotFoundError:
        print("-> user non connecté")

    if not loader.context.is_logged_in:
        loader.interactive_login(user)
        loader.save_session_to_file()

    print("-> connected")

    p = instaloader.Profile.from_username(loader.context, account)

    #f = open(account+"_relations.txt", 'a')

    relations = []

    for fers in p.get_followers():
        print(p.username, "followers:", "->", fers)
        relations.append(fers.username)
    
    for fees in p.get_followees():
        print(p.username, "followees:", "->", fees)
        relations.append(fees.username)

    #for acc in relations:
    #    f.write(acc+"\n")

    print("-> Terminé !")
    return relations

def get_email(account, proxy):
    regex=r"(?<=Please check  ).*(?= for a link)"

    cookies = {'ig_cb':'1', 'ig_did':'C2F50380-DB8E-4A19-95E2-FF591020EE73', 'csrftoken':'i8q12DOIlufeI7t9F4IXoEBvh5wBf3Jm', 'mid':'X2fOVwAEAAEdGUbZHbersq6IptrS'}

    data = {'email_or_username' : account,'recaptcha_challenge_field' : ''}

    headers = {'X-CSRFToken':'i8q12DOIlufeI7t9F4IXoEBvh5wBf3Jm', 'X-Instagram-AJAX': 'a8bd5418e182', 'X-IG-App-ID': '936619743392459'}

    try:
        if proxy == None:
            r = requests.post('https://www.instagram.com/accounts/account_recovery_send_ajax/', data, cookies=cookies, headers=headers, timeout=10)
        else:
            r = requests.post('https://www.instagram.com/accounts/account_recovery_send_ajax/', data, cookies=cookies, headers=headers, proxies=proxy, timeout=10)
      

        #print("-> debug: ",r.text)

        if "We couldn't reach your email address." in r.text or "Sorry, we can't send you a link to reset your password." in r.text:
            return "Impossible"
        elif "\"spam\": true" in r.text:
            global proxies
            proxies.remove(proxy)
    
        infos = re.findall(regex,r.text)[0]
        return infos
    except Exception as e:
        return None

def get_relations_mail(account):
    files = {}
    rel = relations(account)

    iden = 0

    print("-> {} relation(s)".format(len(rel)))

    if os.path.isfile("./{}_results.csv".format(account)):
        f = open(account+"_results.csv", 'r')
        lines = f.readlines()
        if len(lines) != 0:
            iden = int(lines[len(lines) - 1].split(";")[0]) + 1
        f.close()
        print("-> reprise à l'index:", iden)

    proxies = import_proxies()
    api = 0

    f = open(account+"_results.csv", 'a')

    for i in range(iden, len(rel)):
        print("-> récupération {}/{} ~ {}%".format(i, len(rel), round(100*i/len(rel), 3)))
        r = rel[i]
        em = get_email(r, proxies[api])
        while em == None:
            print("-> erreur, changement de proxy ...")
            api = (api + 1) % len(proxies)
            print("-> index proxy actuel:", api, "len proxies:", len(proxies))
            time.sleep(3)
            em = get_email(r, proxies[api])

        files[r] = em
        print(r, "->", em)
        f.write("{};{};{}\n".format(i, r, em))
        f.flush()

    f.close()

    print("-> Términé (100%)")

def main():
    if len(sys.argv) == 2:
        if sys.argv[1] == "search":
            account = sys.argv[2]
            get_relations_mail(account)
        else:
            print("-> usage: ./antikira search <compte>")
    else:
        print("-> usage: ./antikira search <compte>")

def __init__(): main()
