from threading import Thread, Lock
import threading
import requests
import argparse
import colorama as clr
import platform
import random
import csv


def test_proxies(lock, proxy_list, proxy_type, output):
    while True:
        # Get proxy
        try:
            with lock:
                proxy_index = random.randint(
                    0, len(proxy_list[proxy_type]) - 1)
                proxy_ip = proxy_list[proxy_type][proxy_index]
                proxy_list[proxy_type].pop(proxy_index)
        except:
            print(clr.Fore.WHITE +
                  f"No more proxies, exiting thread {threading.current_thread().name}")
            return

        # Init request
        request_code = requests.get("http://example.com", proxies={
            proxy_type: f"{proxy_type}: // {proxy_ip}",
        }).status_code

        if request_code == 200:
            file = open(output, "a", newline="")
            with lock:
                print(clr.Fore.GREEN + f"[+] {proxy_type} {proxy_ip} is good!")
                with file:
                    write = csv.writer(file)
                    write.writerow([proxy_type, proxy_ip])
        else:
            with lock:
                print(clr.Fore.RED + f"[-] {proxy_type} {proxy_ip} is bad!")


def main():
    # Create dict
    proxy_list = {
        "socks4": [],
        "socks5": [],
        "http": []
    }

    # Load all proxies
    try:
        with open(args.socks4, "r") as f:
            contents = f.read().splitlines()
            proxy_list["socks4"] = contents
            print(clr.Fore.GREEN +
                  f"Loaded {len(contents)} Socks 4 proxies succesfully")
    except FileNotFoundError:
        print(clr.Fore.YELLOW +
              "Socks 4 location isn't provided or is invalid, skipping...")

    try:
        with open(args.socks5, "r") as f:
            contents = f.read().splitlines()
            proxy_list["socks5"] = contents
            print(clr.Fore.GREEN +
                  f"Loaded {len(contents)} Socks 5 proxies succesfully")
    except FileNotFoundError:
        print(clr.Fore.YELLOW +
              "Socks 5 location isn't provided or is invalid, skipping...")
    try:
        with open(args.http, "r") as f:
            contents = f.read().splitlines()
            proxy_list["http"] = contents
            print(clr.Fore.GREEN +
                  f"Loaded {len(contents)} HTTP proxies succesfully")
    except FileNotFoundError:
        print(clr.Fore.YELLOW +
              "HTTP location isn't provided or is invalid, skipping...")

    # Start threads
    lock = Lock()
    thread_list = []
    for _ in range(args.thread_count):
        t = Thread(target=test_proxies, args=(
            lock, proxy_list, "socks4", args.output_file))
        thread_list.append(t)
        t = Thread(target=test_proxies, args=(
            lock, proxy_list, "socks5", args.output_file))
        thread_list.append(t)
        t = Thread(target=test_proxies, args=(
            lock, proxy_list, "http", args.output_file))
        thread_list.append(t)

    for t in thread_list:
        t.start()


if __name__ == "__main__":
    # Init colorama if using Windows
    if platform.system() == "Windows":
        print("WINDOWS DETECTED! INITIALIZING COLORAMA")
        clr.init()

    parser = argparse.ArgumentParser()

    parser.add_argument("-s4", "--socks4", dest="socks4",
                        help="Socks 4 proxy list location", type=str, default="")
    parser.add_argument("-s5", "--socks5", dest="socks5",
                        help="Socks 5 proxy list location", type=str, default="")
    parser.add_argument("--http", dest="http",
                        help="HTTP proxy list location", type=str, default="")
    parser.add_argument("-t", "--threads", dest="thread_count",
                        help="Thread count for every proxy type (default: 50)", type=int, default=50)
    parser.add_argument("-o", "--output", dest="output_file",
                        help="CSV file to output proxy results", type=str, required=True)

    args = parser.parse_args()

    # Check is even one proxy arg provided
    if args.socks4 + args.socks5 + args.http == "":
        print(clr.Fore.RED + "You need to provide at least one proxy source!")
        exit(1)

    main()
