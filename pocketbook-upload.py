#!/usr/bin/python3

import requests
import json
import os
import shutil
import subprocess
import sys

# var's

username = 'mail'
password = 'password'

# 
mytoken = ''


def get_token(username,password):
  url = "https://cloud.pocketbook.digital/api/v1.0/auth/login/pocketbook_de"
  # hardcoded client id & secret from main page
  payload = 'shop_id=1&username=' + username + '&password=' + password +'&client_id=qNAx1RDb&client_secret=K3YYSjCgDJNoWKdGVOyO1mrROp3MMZqqRNXNXTmh&grant_type=password&language=de'
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
  }

  response = requests.request("POST", url, headers=headers, data=payload)
  myjson = json.loads(response.text)

  if 'access_token' in myjson:
      #print(json.dumps(myjson, indent=4))
      print("Token: " + myjson['access_token'] )
      return(str(myjson['access_token']))
  else:
      print('[ERROR] faild to get token')
      exit(-1)


def get_books(token=mytoken):
    url = "https://cloud.pocketbook.digital/api/v1.0/books?limit=99999"

    payload = {}
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Authorization': 'Bearer ' + mytoken
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    myjson = json.loads(response.text)
    items = myjson['items']
    if 'total' in myjson:
        #print(json.dumps(myjson, indent=4))
        print("Books: " + str(myjson['total']) )
        return (items)
    else:
        print('[ERROR] faild to get books')
        exit(-1)



def rm_book(token=mytoken,fasthash=""):

    url = "https://cloud.pocketbook.digital/api/v1.1/fileops/delete/?fast_hash=" + fasthash

    payload = {}
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Bearer ' + mytoken
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    if response.text == 'OK':
        print("Deleted" + fasthash)
        #exit(1)
        

def rm_read_books(token=mytoken):
    items = get_books(token=mytoken)
    for book in items:
        if str(book['read_status']) == 'read':
            print(book['title'])
            rm_book(fasthash=book['fast_hash'])
            

def rm_all_books(token=mytoken):
    items = get_books(token=mytoken)
    for book in items:
        #if str(book['read_status']) == 'read':
        print(book['title'])
        rm_book(fasthash=book['fast_hash'])



def upload_book(token=mytoken,filepath=""):
    if not os.path.exists(filepath):
        print("file not found")
        exit(-1)

    filename = os.path.basename(filepath)
    url = "https://cloud.pocketbook.digital/api/v1.1/files/" + filename

    # Define the file path
    headers = {
        'Authorization': 'Bearer ' + mytoken
    }

    # Open the file in binary mode and upload it
    with open(filepath, 'rb') as file:
        response = requests.put(url,  headers=headers, data=file)

    myjson = json.loads(response.text)
    if 'error_code' in myjson:
        #print(json.dumps(myjson, indent=4))
        print("Error: " + str(myjson['error_msg']) )
    else:
        print('[Upload] Success ' + filename)
   

if len(sys.argv) < 2:
    print("<file-to-upload>")
    sys.exit(1)
    # Get the source file and destination directory from command-line arguments

source_path = sys.argv[1]
mytoken = get_token(username=username,password=password)
upload_book(token=mytoken,filepath=source_path)
