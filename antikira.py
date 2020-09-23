#!/bin/python3

import instaloader
import torrequest
import subprocess
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

def change_vpn():
    print("-> VPN ...")
    cmd = ["/usr/bin/sudo", "/usr/local/bin/protonvpn", "connect", "-r"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    for line in process.stdout:
        print("-> vpn:", line.decode("utf-8").strip())
    process.wait()
    print("-> finish errcode =", process.returncode)

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

    print("-> Terminé")
    return relations

def get_email(account, proxy, tor):
    regex=r"(?<=Please check  ).*(?= for a link)"

    cookies = {'ig_cb':'1', 'ig_did':'C2F50380-DB8E-4A19-95E2-FF591020EE73', 'csrftoken':'i8q12DOIlufeI7t9F4IXoEBvh5wBf3Jm', 'mid':'X2fOVwAEAAEdGUbZHbersq6IptrS'}

    data = {'email_or_username' : account,'recaptcha_challenge_field' : ''}

    headers = {'X-CSRFToken':'i8q12DOIlufeI7t9F4IXoEBvh5wBf3Jm', 'X-Instagram-AJAX': 'a8bd5418e182', 'X-IG-App-ID': '936619743392459'}

    try:
        if tor != None:
            r = tor.post('https://www.instagram.com/accounts/account_recovery_send_ajax/', data, cookies=cookies, headers=headers, timeout=10)
        elif proxy == None:
            r = requests.post('https://www.instagram.com/accounts/account_recovery_send_ajax/', data, cookies=cookies, headers=headers, timeout=10)
        else:
            r = requests.post('https://www.instagram.com/accounts/account_recovery_send_ajax/', data, cookies=cookies, headers=headers, proxies=proxy, timeout=10)
      
        print("-> debug: ",r.text)

        if "We couldn't reach your email address." in r.text or "Sorry, we can't send you a link to reset your password." in r.text:
            #return "Impossible"
            return None
        elif "\"spam\": true" in r.text:
            global proxies
            proxies.remove(proxy)
            print("-> proxy spam: true, suppression.")
            return None
    
        infos = re.findall(regex,r.text)[0]
        return infos
    except Exception as e:
        print(e)
        return None

def get_relations_mail(rel, output):
    files = {}
    iden = 0

    print("-> {} relation(s)".format(len(rel)))

    if os.path.isfile("./{}_results.csv".format(output)):
        f = open(output+"_results.csv", 'r')
        lines = f.readlines()
        if len(lines) != 0:
            iden = int(lines[len(lines) - 1].split(";")[0]) + 1
        f.close()
        print("-> reprise à l'index:", iden)

    #proxies = import_proxies()
    #api = 0

    tor = torrequest.TorRequest(password='16:333F3E9CD8B5062E60233486ABE1F06B459A43DF6737E12116631FEB5C')

    f = open(output+"_results.csv", 'a')

    for i in range(iden, len(rel)):
        print("-> récupération {}/{} ~ {}%".format(i, len(rel), round(100*i/len(rel), 3)))
        r = rel[i]
        em = get_email(r, None, tor)
        while em == None:
            print("-> erreur, changement de proxy ...")
            #api = (api + 1) % len(proxies)
            #print("-> index proxy actuel:", api, "len proxies:", len(proxies))
            time.sleep(1)
            #change_vpn()
            print("-> TOR nouvelle identité")
            tor.reset_identity()
            em = get_email(r, None, tor)

        files[r] = em
        print(r, "->", em)
        f.write("{};{};{}\n".format(i, r, em))
        f.flush()

    f.close()

    print("-> Terminé (100%)")

def merge(fileBig, fileLittle):
    profilesBase = {}
    outputfile = fileBig+"-merge.csv"
    with open(fileBig, 'r') as fb:
        lines = fb.readlines()
        for line in lines:
            data = line.split(";")
            profilesBase[data[1]] = data[2]
    

    with open(fileLittle, 'r') as fl:
        lines = fl.readlines()
        for line in lines:
            data = line.split(";")
            if data[1] in profilesBase.keys():
                if profilesBase[data[1]].strip() == "Impossible" and data[2].strip() != "Impossible":
                    profilesBase[data[1]] = data[2]
                    print("-> merge {} <- {};{}".format(outputfile, data[1], data[2].strip()))


    with open(outputfile, 'w') as fo:
        c = 0
        for k,v in profilesBase.items():
            fo.write("{};{};{}".format(c, k, v))
            c += 1

    print("-> Terminé")

def main():
    if len(sys.argv) == 4:
        if sys.argv[1] == "merge":
            big = sys.argv[2]
            little = sys.argv[3]

            if not (os.path.isfile("./{}".format(big)) and os.path.isfile("./{}".format(little))):
                print("-> fichiers inxistants")
                sys.exit(1)

            merge(big, little)
    elif len(sys.argv) == 3:
        if sys.argv[1] == "search":
            account = sys.argv[2]
            rel = relations(account)
            get_relations_mail(rel, account)
        elif sys.argv[1] == "research":
            filename = sys.argv[2]
            if not os.path.isfile("./{}".format(filename)):
                print("-> fichier inexistant")
                sys.exit(1)

            with open(filename, 'r') as f:
                lines = f.readlines()
                rel = [l.split(';')[1] for l in lines]
                get_relations_mail(rel, filename+"-research")
        else:
            print("-> usage: ./antikira merge <fichierBase> <fichierInclusion>")
            print("-> usage: ./antikira search <compte>")
            print("-> usage: ./antikira research <fichier>")
    else:
        print("-> usage: ./antikira merge <fichierBase> <fichierInclusion>")
        print("-> usage: ./antikira search <compte>")
        print("-> usage: ./antikira research <fichier>")

if __name__ == "__main__":  main()
