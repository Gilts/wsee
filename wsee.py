import requests,re
from requests.exceptions import ReadTimeout, Timeout, ConnectionError, ChunkedEncodingError, TooManyRedirects, InvalidURL
import os, fnmatch; os.system("clear")
import csv
from collections import defaultdict
import traceback
from os.path import abspath, dirname
from multiprocessing import Process, cpu_count, Manager
from time import sleep
from concurrent.futures import ThreadPoolExecutor

expected_response = 101
cflare_domain = "id3.sshws.me"
cfront_domain = "d3r0orex98gi31.cloudfront.net"
payloads = { "Host": cfront_domain, "Upgrade": "websocket", "DNT":  "1", "Accept-Language": "*", "Accept": "*/*", "Accept-Encoding": "*", "Connection": "keep-alive, upgrade", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36" }
wsocket = { "Connection": "Upgrade", "Sec-Websocket-Key": "dXP3jD9Ipw0B2EmWrMDTEw==", "Sec-Websocket-Version": "13", "Upgrade": "websocket" }
switch = { "dir": "0", "func": "0" }
hostpath = 'host'
logpath = 'logs'
outpath = 'output'

columns = defaultdict(list)
txtfiles= []
Resultee=[]
Faily=[]

class colors:
	RED_BG = '\033[41m\033[1m'
	GREEN_BG = '\033[42m'
	ENDC = '\033[m'

def doma():
	global frontdom
	print("1. Custom Domain")
	print("2. Default CloudFront")
	print("3. Default CloudFlare")
	print("Q to Quit")
	print("M to Menu")
	print("")
	ansi=input(" Choose Option : ").lower()
	print("")
	if str(ansi)=="1":
		domain=input(" Domain : ")
		payloads["Host"]=f"{domain}"
	elif str(ansi)=="2":
		payloads["Host"]=f"{cfront_domain}"
	elif str(ansi)=="3":
		payloads["Host"]=f"{cflare_domain}"
	elif str(ansi)=="q":
		exit()
	elif str(ansi)=="m":
		menu()
	else:
		print("["+colors.RED_BG+" GGRRR! " + colors.ENDC + "] Invalid INPUT!" )
		print("")
		menu()
	frontdom = str(payloads["Host"])
	print("["+colors.GREEN_BG + f" {frontdom} "+ colors.ENDC + "] Selected as Domain Fronting!")
	print("["+colors.RED_BG+" Warning! " + colors.ENDC + "] : [" + colors.RED_BG + " INVALID " + colors.ENDC + "] Domain Will Give 0 Result!" )
	print("")
	return

def filet():
	global domainlist, fileselector
	num_file = 1
	print("1. Check Files in Host Folder")
	print("2. Check Files in Current Folder")
	print("q to Quit")
	print("m to Menu")
	print("")
	ans=input(" Choose : ").lower()
	if ans=="1":
		files = os.listdir(hostpath)
		switch["dir"]="0"
	elif ans=="2":
		files = [f for f in os.listdir('.') if os.path.isfile(f)]
		switch["dir"]="1"
	elif ans=="q":
		exit()
	elif ans=="m":
		menu()
	else:
		filet()
	print(" [" + colors.RED_BG + " Files Found " + colors.ENDC + "] ")
	for f in files:
		if fnmatch.fnmatch(f, '*.txt'):
			print( str(num_file),str(f))
			num_file=num_file+1
			txtfiles.append(str(f))
	print("")
	print(" M back to Menu ")
	fileselector = input(" Choose Target Files : ")
	if fileselector.isdigit():
		print("")
		print(" Target Chosen : " + colors.RED_BG + " "+txtfiles[int(fileselector)-1]+" "+colors.ENDC)
		direct = str(switch["dir"])
		if direct == "0":
			file_hosts = str(hostpath) +"/"+ str(txtfiles[int(fileselector)-1])
		else:
			file_hosts = str(txtfiles[int(fileselector)-1])
	else:
		menu()

	with open(file_hosts) as f:
		parseddom = f.read().split()
	domainlist = list(set(parseddom))
	domainlist = list(filter(None, parseddom))
	print(" Total of Domains Loaded: " + colors.RED_BG + " " +str(len(domainlist)) + " "+colors.ENDC )
	print("")
	return

def csveat():
	global domainlist, fileselector
	num_file=1
	print("1. Check Files in Host Folder")
	print("2. Check Files in Current Folder")
	print("q to Quit")
	print("m to Menu")
	print("")
	ans=input(" Choose : ").lower()
	if ans=="1":
		files = os.listdir(hostpath)
		switch["dir"]="0"
	elif ans=="2":
		files = [f for f in os.listdir('.') if os.path.isfile(f)]
		switch["dir"]="1"
	elif ans=="q":
		exit()
	elif ans=="m":
		menu()
	else:
		csveat()
	print(" [" + colors.RED_BG + " Files Found " + colors.ENDC + "] ")
	for f in files:
		if fnmatch.fnmatch(f, '*.csv'):
			print( str(num_file),str(f))
			num_file=num_file+1
			txtfiles.append(str(f))
	print("")
	print(" M back to Menu ")
	fileselector = input(" Choose Target Files : ")
	if fileselector.isdigit():
		print("")
		print(" Target Chosen : " + colors.RED_BG + " "+txtfiles[int(fileselector)-1]+" "+colors.ENDC)
		direct = str(switch["dir"])
		if direct == "0":
			file_hosts = str(hostpath) +"/"+ str(txtfiles[int(fileselector)-1])
		else:
			file_hosts = str(txtfiles[int(fileselector)-1])
	else:
		menu()

	with open(file_hosts,'r') as csv_file:
		reader = csv.reader(csv_file)
		for row in reader:
			for (i,v) in enumerate(row):
				columns[i].append(v)
	parseddom=columns[9]+columns[3]
	domainlist = list(set(parseddom))
	domainlist = list(filter(None, parseddom))
	print(" Total of Domains Loaded: " + colors.RED_BG + " " +str(len(domainlist)) + " "+colors.ENDC )
	print("")
	return

def executor():
	with Manager() as manager:
		global Resultee, Faily
		num_cpus = cpu_count()
		processes = []
		Resultee = manager.list()
		Faily = manager.list()
		for process_num in range(num_cpus):
			section = domainlist[process_num::num_cpus]
			p = Process(target=engine, args=(section,nametag,headers))
			p.start()
			processes.append(p)
		for p in processes:
			p.join()
		Resultee = list(Resultee)
		Faily = list(Faily)
		print("")
		print(" Failed Result : "  + colors.RED_BG + " "+str(len(Faily)) +" "+ colors.ENDC )
		print(" Successfull Result : " + colors.GREEN_BG + " "+str(len(Resultee))+ " "+colors.ENDC)
		return

def Asyncutor():
	try:
		num_cpus = cpu_count()
		with ThreadPoolExecutor(max_workers=num_cpus) as executor:
			if switch["func"]=="0":
				executor.submit(engine(domainlist,nametag,headers))
			else:
				executor.submit(grabber(domainlist,nametag,headers))
			executor.shutdown( cancel_futures = True )
	except Exception as e:
		print(e)
		traceback.print_exc()
		pass
	print("")
	print(" Failed Result : "  + colors.RED_BG + " "+str(len(Faily)) +" "+ colors.ENDC )
	print(" Successfull Result : " + colors.GREEN_BG + " "+str(len(Resultee))+ " "+colors.ENDC)
	return
 
def uinput():
	print("")
	print("Scanning Finished!")
	print("1. Go Back to Menu")
	print("2. Scanning Again")
	print("3. Quit Instead")
	print("")
	ans=input("Choose Option: ")
	if ans=="2":
		return
	elif ans=="3":
		exit()
	else:
		menu()

def hacki():
	global domainlist, subd
	subd = input("\nInput Domain: ")
	subd = subd.replace("https://","").replace("http://","")
	r = requests.get("https://api.hackertarget.com/hostsearch/?q=" + subd, allow_redirects=False)
	if r.text == "error invalid host":
		exit("ERR: error invalid host")
	else:
		domainlist = re.findall("(.*?),",r.text)
		return

def engine(domainlist,nametag,headers):
	for domain in domainlist:
		try:
			r = requests.get("http://" + domain, headers=headers, allow_redirects=False)
			if r.status_code == expected_response:
				print(" ["+colors.GREEN_BG+" HIT "+colors.ENDC+"] " + domain)
				print(domain, file=open(f"{nametag}.txt", "a"))
				Resultee.append(str(domain))
			elif r.status_code != expected_response:
				print(" ["+colors.RED_BG+" FAIL "+colors.ENDC+"] " + domain + " [" +colors.RED_BG+" " + str(r.status_code) + " "+colors.ENDC+"]")
				Faily.append(str(domain))
		except (Timeout, ReadTimeout, ConnectionError):
			print(" ["+colors.RED_BG+" FAIL "+colors.ENDC+"] " + domain + " [" + colors.RED_BG +" TIMEOUT "+colors.ENDC+"]")
			Faily.append(str(domain))
			pass
		except(ChunkedEncodingError):
			print(" ["+colors.RED_BG+" FAIL "+colors.ENDC+"] " + domain + " [" + colors.RED_BG+" Invalid Length "+colors.ENDC + "]")
			Faily.append(str(domain))
			pass
		except(TooManyRedirects):
			print(" ["+colors.RED_BG+" FAIL "+colors.ENDC+"] " + domain + " [" +colors.RED_BG+" Redirects Loop "+colors.ENDC+"]")
			Faily.append(str(domain))
			pass
		except(InvalidURL):
			print(" ["+colors.RED_BG+" FAIL "+colors.ENDC+"] " + domain + " [" +colors.RED_BG+" Invalid URL "+colors.ENDC+"]")
			Faily.append(str(domain))
			pass
		except Exception as e:
			print(e)
			traceback.print_exc()
			pass

def grabber(domainlist,nametag,headers):
	for domain in domainlist:
		try:
			commando =f"cat {domain} | ./zgrab2 http --custom-headers-names='Upgrade,Sec-WebSocket-Key,Sec-WebSocket-Version,Connection' --custom-headers-values='websocket,dXP3jD9Ipw0B2EmWrMDTEw==,13,Upgrade' --remove-accept-header --dynamic-origin --use-https --port 443 --max-redirects 10 --retry-https --cipher-suite portable -t 10 | | jq '.data.http.result.response.status_code,.domain' | grep -A 1 -E --line-buffered '^101'"
			result = subprocess.check_output(commando, shell=True)
			print(result)
		except Exception as e:
			print(e)
			traceback.print_exc()
			print("")
			print(colors.RED_BG + " Check your  ZGrab Installation " + colors.ENDC)
			menu()

def menu():
	print('''

__  _  ________ ____   ____  
\ \/ \/ /  ___// __ \_/ __ \ 
 \     /\___ \\  ___/\  ___/ 
  \/\_//____  >\___  >\___  >
			\/     \/     \/  

	''')
	print("    [" + colors.RED_BG + " Domain : Fronting " + colors.ENDC + "]")
	print("     ["+colors.RED_BG+" Author " + colors.ENDC + ":" + colors.GREEN_BG + " Kiynox " + colors.ENDC + "]")
	print("")

	print("1. CDN Websocket")
	print("2. Local Websocket")
	print("3. ZGrab Websocket")
	print("q to Quit")
	print("")
	ans=input(" Choose Option : ")
	print("")
	if str(ans)=="1":
		print("1. Scan .TXT")
		print("2. Scan .CSV")
		print("3. Scan Online Sub-Domain Enumeration [HackerTarget]")
		print("Q to Quit")
		print("M to Menu")
		print("")
		opsi=input(" Choose Option :  ").lower()
		print("")
		switch["func"]="0"
		if str(opsi)=="1":
			def text():
				global headers, nametag
				headers = payloads
				doma()
				filet()
				nametag = str(txtfiles[int(fileselector)-1]).removesuffix(".txt") + f"-[{frontdom}]-[CDN]-[TXT]"
				executor()
				uinput()
				text()
			text()
		elif str(opsi)=="2":
			def csv():
				global headers, nametag
				headers = payloads
				doma()
				csveat()
				nametag = str(txtfiles[int(fileselector)-1]).removesuffix(".csv") + f"-[{frontdom}]-[CDN]-[CSV]"
				Asyncutor()
				uinput()
				csv()
			csv()
		elif str(opsi)=="3":
			def enum():
				global headers, nametag
				headers = payloads
				doma()
				hacki()
				nametag = str(subd) + f"-[{frontdom}]-[CDN]-[ENUM]"
				Asyncutor()
				uinput()
				enum()
			enum()
		elif str(opsi)=="m":
			menu()
		else:
			exit()

	elif str(ans)=="2":
		print("1. Scan .TXT")
		print("2. Scan .CSV")
		print("3. Scan Online Sub-Domain Enumeration [HackerTarget]")
		print("Q to Quit")
		print("M to Menu")
		print("")
		opsi=input(" Choose Option :  ")
		print("")
		switch["func"]="0"
		if str(opsi)=="1":
			def localtext():
				global headers
				headers = wsocket
				filet()
				nametag = str(txtfiles[int(fileselector)-1]).removesuffix(".txt") + "-[LOCAL]-[TXT]"
				Asyncutor()
				uinput()
				localtext()
			localtext()
		elif str(opsi)=="2":
			def localcsv():
				global headers
				headers = wsocket
				csveat()
				nametag = str(txtfiles[int(fileselector)-1]).removesuffix(".csv") + "-[LOCAL]-[CSV]"
				Asyncutor()
				uinput()
				localcsv()
			localcsv()
		elif str(opsi)=="3":
			def localenum():
				global headers
				headers = wsocket
				hacki()
				nametag = str(subd) + "-[LOCAL]-[ENUM]"
				Asyncutor()
				uinput()
				localenum()
			localenum()
		elif str(opsi)=="m":
			menu()
		else:
			exit()

	elif str(ans)=="3":
		print("1. Scan .TXT")
		print("2. Scan .CSV")
		print("3. Scan Online Sub-Domain Enumeration [HackerTarget]")
		print("Q to Quit")
		print("M to Menu")
		print("")
		opsi=input(" Choose Option :  ")
		print("")
		switch["func"]="1"
		if str(opsi)=="1":
			def grabtext():
				filet()
				nametag = str(txtfiles[int(fileselector)-1]).removesuffix(".txt") + "-[LOCAL]-[TXT]"
				Asyncutor()
				uinput()
				localtext()
			grabtext()
		elif str(opsi)=="2":
			def grabcsv():
				csveat()
				nametag = str(txtfiles[int(fileselector)-1]).removesuffix(".csv") + "-[LOCAL]-[CSV]"
				Asyncutor()
				uinput()
				localcsv()
			grabcsv()
		elif str(opsi)=="3":
			def grabenum():
				hacki()
				nametag = str(subd) + "-[LOCAL]-[ENUM]"
				Asyncutor()
				uinput()
				localenum()
			grabenum()
		elif str(opsi)=="m":
			menu()
		else:
			exit()

	else:
		exit()

if __name__ == '__main__':
	os.chdir(dirname(abspath(__file__)))
	if not os.path.exists(hostpath):
		os.makedirs(hostpath)
	menu()