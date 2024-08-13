import os
import time
import requests
from datetime import datetime
from colorama import init, Fore, Style
from concurrent.futures import ThreadPoolExecutor
import random
from collections import deque

init(autoreset=True)

def clear_console():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def load_proxies(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines()]

def get_random_proxy(proxies, recent_proxies):
    proxy = random.choice(proxies)
    while proxy in recent_proxies:
        proxy = random.choice(proxies)
    return proxy


def send_request_friend(session, accs_id, user_id, proxies, recent_proxies, current_request, total_requests):
    pdata = {'user_id': user_id}
    success = False
    while not success:
        proxy_str = get_random_proxy(proxies, recent_proxies)
        proxy = {'http': proxy_str, 'https': proxy_str}
        try:
            response = session.post(f'https://www.kogama.com/user/{accs_id}/friend', json=pdata, proxies=proxy, timeout=4)
            if response.status_code in [200, 201, 204]:
                print(Fore.GREEN + f"Friend request sent to profile ID: {user_id} [{current_request}/{total_requests}]")
                success = True
            elif response.status_code == 429:
                print(Fore.RED + "Too many requests. Trying a different proxy...")
            else:
                print(Fore.RED + f"Failed to send friend request: {response.status_code}")
                success = True
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
            print(Fore.RED + "Connection error. Trying a different proxy...")

    recent_proxies.append(proxy_str)
    if len(recent_proxies) > 30:
        recent_proxies.popleft()

def auth_account(session, username, password, user_id, proxies, recent_proxies, current_request, total_requests):
    proxy_str = get_random_proxy(proxies, recent_proxies)
    proxy = {'http': proxy_str, 'https': proxy_str}

    datak = {
        'username': username,
        'password': password
    }

    aut = session.post('https://www.kogama.com/auth/login/', json=datak, proxies=proxy, timeout=4)

    if aut.status_code == 200:
        send_request_friend(session, aut.json()['data']['id'], user_id, proxies, recent_proxies, current_request, total_requests)
    else:
        print(Fore.RED + f"Account login failed for {username}")

    recent_proxies.append(proxy_str)
    if len(recent_proxies) > 30:
        recent_proxies.popleft()

def mass_friend_requests_sender():
    proxies = load_proxies('C:\\Users\\xazit\\Desktop\\Mass Friend\\proxies.txt')
    recent_proxies = deque(maxlen=30)

    with open('C:\\Users\\xazit\\Desktop\\Mass Friend\\friendaccs.txt', encoding='utf-8') as f:
        accounts = [line.strip() for line in f.readlines()]

    user_id = input(Fore.YELLOW + "Enter the player PID to send friend requests to: ")
    total_requests = int(input(Fore.YELLOW + "Friend requests number: "))

    current_request = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for account in accounts:
            if ':' not in account:
                continue
            if current_request >= total_requests:
                break
            username, password = account.split(':')
            current_request += 1
            session = requests.Session()
            futures.append(executor.submit(auth_account, session, username, password, user_id, proxies, recent_proxies, current_request, total_requests))
            if current_request % 10 == 0:
                print(Fore.MAGENTA + f"Initializing proxies.. ({current_request/total_requests:.2%}, {current_request}/{total_requests})", end='\r')

        for future in futures:
            future.result()



def main_menu():
    clear_console()
    print(Fore.BLUE + "Welcome.")
    time.sleep(1)
    print(" ")
    print(Fore.RED + "1. " + Fore.YELLOW + "Mass friend requests")
    time.sleep(0.3)
    print(Fore.RED + "2. " + Fore.YELLOW + "None")
    print(" ")
    time.sleep(0.3)

    choice = input(Fore.RED + "     > ")

    if choice == '1' or choice == '01':
        clear_console()
        mass_friend_requests_sender()
        input("Press enter to continue..")
        main_menu()

    else:
        print(Fore.RED + "Invalid choice")
        time.sleep(0.4)
        print(Fore.RED + "Returning to main menu..")
        time.sleep(1.4)

main_menu()
