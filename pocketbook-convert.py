import requests
import json
import os
import shutil
import subprocess
import sys

username = 'name'
password = 'pass'
mytoken = ''


def get_token(username,password):
  url = "https://cloud.pocketbook.digital/api/v1.0/auth/login/pocketbook_de"

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
    #convert_book(filepath=filepath)

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
   

def convert_book(filepath=""):
    myacbt = check_acbt()
    mykcc = check_kcc()
    filename = os.path.basename(filepath)
    filebase, extension = os.path.splitext(filename)

    if mykcc != "failed":
        print("kcc found")
        
    if myacbt != "failed":
        print("acbt found")    

    if os.path.exists(filebase):
        command = f'rm -fR "{filebase}"'  # or any other command you want to run
        subprocess.run(command, shell=True, capture_output=True, text=True)  
             
# Define a command to execute the binary
    command = f'{myacbt} extract --output-folder "{os.path.abspath(filebase)}" -co true -iq 60 -s 50 "{filepath}"'  # or any other command you want to run
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    #print('Return code:', result.stderr)
    if os.path.exists(filepath):
        try:
            shutil.move(filepath, filebase + "_old.bak")
            print(f'File moved from {filename} to ' + filebase +  "_old.bak")
        except FileNotFoundError:
            print(f'The file {filename} does not exist.')
        except Exception as e:
            print(f'Error moving file: {e}')
    #filepath = 
    #print(f'{os.path.abspath(filebase)} + {os.path.abspath(filebase)}')
    if os.path.exists(filebase):
        print(f"Convert:" + os.path.abspath(filebase) )
        command = f'{mykcc} -o "{filepath}" --dedupecover --forcecolor -f CBZ -c 2 -r 1 -g 0 -s -u -m "{os.path.abspath(filebase)}"'
#        command = f'{mykcc} --dedupecover --forcecolor -f CBZ -c 2 -r 1 -g 0 -s -u -m "{filebase}"'  # or any other command you want to run
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print('Return code:', result.stdout)
    if not os.path.exists(filepath):
        print(f'ERROR on {filepath}')
        try:
            shutil.move(filebase + "_old.bak" , filepath )
        except FileNotFoundError:
            print(f'The file {filename} does not exist.')
        except Exception as e:
            print(f'Error moving file: {e}')
        exit(-1)

    if os.path.exists(filebase):
        command = f'rm -fR "{filebase}"'  # or any other command you want to run
        subprocess.run(command, shell=True, capture_output=True, text=True)  
    
        # kcc-c2e --dedupecover --forcecolor -f CBZ -c 2 -r 1 -g 0 -s -u -m
        #binary_name =  
    # Print the command output
    #print('Return code:', result.returncode)
    #print('Output:', result.stdout)
    #print('Error (if any):', result.stderr)

def check_kcc():

    # Define the name of the binary
    binary_name = 'kcc-c2e'

    # Check if the binary is in the PATH
    binary_path = shutil.which(binary_name)

    if binary_path:
        #print(f'The binary "{binary_name}" is located at: {binary_path}')
        return(binary_name)
    else:
        return("failed")



def check_acbt():

    # Define the name of the binary
    binary_name = 'acbt'

    # Check if the binary is in the PATH
    binary_path = shutil.which(binary_name)

    if binary_path:
        print(f'The binary "{binary_name}" is located at: {binary_path}')
        return(binary_name)
    else:
        if os.path.exists('./acbt'):
            binary_name =  os.path.abspath('./acbt')
            return(binary_name)

        command = f'wget https://github.com/binarynonsense/comic-book-tools/releases/latest/download/ACBT_Linux.zip && unzip -o ACBT_Linux && cp -R ACBT_Linux/* . && rm -fR ACBT_*'  # or any other command you want to run

        # Execute the command
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if  os.path.exists("./acbt"):
            print("acbt installed")
            binary_name =  os.path.abspath('./acbt')
            return(binary_name)
        else:
            print("\t Install acbt:\n\t\twget https://github.com/binarynonsense/comic-book-tools/releases/latest/download/ACBT_Linux.zip && unzip -o ACBT_Linux && sudo cp -R ACBT_Linux/* /usr/local/ && rm -fR ACBT_* ")
            return("failed")

        if not binary_path:
            print("\t Install acbt:\n\t\twget https://github.com/binarynonsense/comic-book-tools/releases/latest/download/ACBT_Linux.zip && unzip -o ACBT_Linux && sudo cp -R ACBT_Linux/* /usr/local/ && rm -fR ACBT_* ")




if len(sys.argv) < 2:
    print("<file-to-upload>")
    sys.exit(1)
    # Get the source file and destination directory from command-line arguments

source_path = sys.argv[1]
#mytoken = get_token(username=username,password=password)
convert_book(filepath=source_path)
