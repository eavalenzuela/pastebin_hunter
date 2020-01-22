import argparse, configparser
import time, sys, requests, json, re

def get_args():
    parser = argparse.ArgumentParser('PastebinHunter: scraping API monitor')
    parser.add_argument('-c', dest='cred_file', help='credentials file')
    parser.add_argument('-s', dest='strings_file', help='search query file (comma, line-delineated)')
    parser.add_argument('--sql', action='store_true', help='store information in sql db specified')
    parser.add_argument('-i', dest='image_directory', help='image directory path')
    parser.add_argument('-l', dest='paste_limit', help='maxiumum number of scrapes to process (omit for unlimited)')
    return parser.parse_args()

def get_pastes():
    api_url = 'https://scrape.pastebin.com/api_scraping.php'
    response = requests.get(api_url)
    api_json = json.loads(response.content)
    return api_json

def process(paste, args, search_strings):
    paste_url = 'https://scrape.pastebin.com/api_scrape_item.php?i='
    response = requests.get(paste_url+paste['key'])
    for query in search_strings:
        if re.search(query, response.content):
            print(response.content)

def monitor_loop(args):
    search_strings = []
    try:
        with open(args.strings_file, 'r') as inf:
            search_strings = inf.readlines()
    except FileNotFoundError as fnfe:
        print('Search query file not found. Exiting.')
        sys.exit(1)
    except IOError as ioe:
        print('I/O error occurred on search query file. Exiting.')
        sys.exit(1)
    if len(search_strings) < 1:
        print('Search query file is emtpy. Exiting.')
        sys.exit(1)

    if not args.paste_limit:
        unlimited = True
    else:
        unlimited = False
        try:
            args.paste_limit = int(args.paste_limit)
        except TypeError as te:
            print('You did not set a valid integer for the -l paste_limit option')
            sys.exit(1)
    keys = []
    while unlimited or len(keys) < args.paste_limit:
        pastes = get_pastes()
        time.sleep(20)
        for paste in pastes:
            if paste['key'] not in keys:
                print(paste['key']+' : '+paste['title'])
                keys.append(paste['key'])
                process(paste, args, search_strings)

def run():
    args = get_args()
    if args.sql:
        import mysql.connector 
    monitor_loop(args)

if __name__ == "__main__":
    run()
