import smtplib
from email import message
import time

import urllib.request
import re
import configparser

IP_NUMBER_RE = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"



def read_cfg():
    config = configparser.ConfigParser()
    config.read("smtp.ini")
    return config["DEFAULT"]

config = read_cfg()
CONTROL_FILE_NAME = config["CONTROL_FILE_NAME"]
CONTROL_FILE_CHECK_FREQUENCY = int(config["CONTROL_FILE_CHECK_FREQUENCY"])
IP_CHECK_FREQUENCY = int(config["IP_CHECK_FREQUENCY"])
IP_FILENAME = config["IP_FILENAME"]
FROM_ADDRESS = config["FROM_ADDRESS"]
TO_ADDRESS = config["TO_ADDRESS"]
SMTP_LOGIN_NAME = config["SMTP_LOGIN_NAME"]
SMTP_LOGIN_PASSWORD = config["SMTP_LOGIN_PASSWORD"]


def print_ip():
    url = "http://checkip.dyndns.org"
    response = urllib.request.urlopen(url)  #.urlopen(url).read()
    response = response.read().decode("utf-8")
    print(response)
    theIP = re.findall(IP_NUMBER_RE, response)
    print(theIP)


def get_ip():
    try:
        url = "http://checkip.dyndns.org"
        response = urllib.request.urlopen(url)  # .urlopen(url).read()
        response = response.read().decode("utf-8")
        return re.findall(IP_NUMBER_RE, response)[0]
    except:
        return "0.0.0.0"


def write_ip_to_file(filename, ip_address):
    with open(filename, "w") as file:
        file.write(ip_address)

def main_loop():
    make_controlfile()
    stop = False
    counter = 0
    current_ip = get_ip()
    print("Initial IP:", get_ip())
    while not stop:
        counter += 1
        if counter % CONTROL_FILE_CHECK_FREQUENCY == 0:
            stop = file_stop()
        if counter % IP_CHECK_FREQUENCY == 0:
            new_ip = get_ip()
            write_ip_to_file(IP_FILENAME, new_ip)
            is_change = new_ip != current_ip
            if is_change:
                send_ip_changed_email()
        time.sleep(1)

def make_controlfile():
    with open(CONTROL_FILE_NAME, "w") as file:
        file.write("RUN")

def file_stop():
    with open(CONTROL_FILE_NAME) as file:
        return "STOP" in file.read()

def send_ip_changed_email(new_ip, old_ip):

    subject = 'IP changed'
    body = 'The server global IP has changed\n' + "New IP: " + new_ip + "\nOld IP: " + old_ip + "\n"

    msg = message.Message()
    msg.add_header('from', FROM_ADDRESS)
    msg.add_header('to', TO_ADDRESS)
    msg.add_header('subject', subject)
    msg.set_payload(body)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(SMTP_LOGIN_NAME, SMTP_LOGIN_PASSWORD)
    server.send_message(msg, from_addr=FROM_ADDRESS, to_addrs=[TO_ADDRESS])



