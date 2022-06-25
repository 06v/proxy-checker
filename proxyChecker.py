import re
import os
import sys
import requests
import time
import threading
from colorama import Fore
from concurrent.futures import ThreadPoolExecutor

print("""

 _____                        _____ _               _             
|  __ \                      / ____| |             | |            
| |__) | __ _____  ___   _  | |    | |__   ___  ___| | _____ _ __ 
|  ___/ '__/ _ \ \/ / | | | | |    | '_ \ / _ \/ __| |/ / _ \ '__|
| |   | | | (_) >  <| |_| | | |____| | | |  __/ (__|   <  __/ |   
|_|   |_|  \___/_/\_/\__, |  \_____|_| |_|\___|\___|_|\_\___|_|   
                                              __/ |                                       
                                             |___/                                        

""")

class proxyChecker:

    def __init__(self, proxyFile, proxyType, threads):
        self.proxyFile = proxyFile
        self.proxyType = proxyType
        self.threads = threads
        self.working = 0
        self.dead = 0
        self.remain = 0
        self.lastRemain = 0
        self.proxys = []

        self.checkThreads()
        self.checkProxyType()
        self.loadProxys()
        self.run()


    def checkThreads(self):

        if self.threads.isdigit():
            self.threads = int(self.threads)
        else:
            print(f"{Fore.RED} [Error]{Fore.RESET} Please input a valid Number!".format(self.threads))
            exit() 

    def checkProxyType(self):

        if self.proxyType != "socks5" and self.proxyType != "https":
            print(f"{Fore.RED} [Error]{Fore.RESET} Please input https or socks5!".format(self.proxyType))
            exit() 

    def loadProxys(self):
        
        if os.path.exists(self.proxyFile) == False:
            print(f"{Fore.RED} [Error]{Fore.RESET} No File found in that Path!".format(self.proxyFile))
            exit()
               
        with open(self.proxyFile) as file:

            for line in file:

                #remove new lines
                line = line.strip()
                
                #check if the current line is an ip adress + port using a regular expression

                if re.match(r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]):[0-9]+$", line):
                    self.proxys.append(line)
                else:
                    print(" [!] Proxy not in right Format!".format(line))


        proxysCount = len(self.proxys)

        if proxysCount == 0:
            print(f"{Fore.RED} [Fail]{Fore.RESET} Is proxies.txt empty?")
            exit() 

        self.remain = proxysCount

        print(" [{Fore.GREEN}*{Fore.RESET}] Loaded {0} lines from {1}".format(proxysCount, self.proxyFile ))


    def checkProxy(self,proxy):

        if self.proxyType == "socks5":
            protocol = "socks5://"

        elif self.proxyType == "https":
            protocol = "https://"

        proxyDict = { 
                "https" : protocol + proxy
        }

        try:

            r = requests.get("https://google.de", proxies=proxyDict, timeout=10)

            if r.ok:    
                self.working += 1
                self.saveProxy(proxy)

        except Exception:
            self.dead += 1

        self.remain -= 1

    
    def saveProxy(self, proxy):
        with open("working_"+self.proxyType+".txt","a") as file:
            file.write(proxy + "\n")


    def printStatistics(self):

        while True:

            if self.lastRemain != self.remain:

                if os.name == "nt":
                    os.system("cls")
                elif os.name == "posix":
                    os.system("clear")

                print(" [+] Working: {0}".format(self.working))
                print(" [-] Dead: {0}".format(self.dead))
                print(" [~] Remaining: {0}".format(self.remain))
                self.lastRemain = self.remain
            
            if self.remain == 0:
                print(f"{Fore.GREEN} Done! Press Enter to Exit.")
                input()
                quit()
                break

            time.sleep(0.05)


    def run(self):

        x = threading.Thread(target=self.printStatistics, args=())
        x.start()
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            
            for proxy in self.proxys:
                executor.submit(self.checkProxy, proxy)



proxyFile = input(" Proxy File Path >> ")
proxyType = input(" Proxy Type (https/socks5) >> ")
threads = input(" Threads >> ")
print("")

checker = proxyChecker(proxyFile,proxyType,threads)
