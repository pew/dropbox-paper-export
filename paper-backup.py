import requests
import json
import os
import sys
import shutil
import argparse

parser = argparse.ArgumentParser(description='Export Dropbox Paper Notes.')
parser.add_argument('-d','--dest', help='Where to store the data.', required=True)
parser.add_argument('-f','--force', help='Force deletion of destination folder.', required=False, action='store_true')
args = parser.parse_args()

try:
    apikey = os.environ['paperApiKey']
except:
    apikey = ''
    if not apikey:
        sys.exit('Print API Key not set')

backup_dir = args.dest

if args.force is True:
    try:
        shutil.rmtree(backup_dir)
    except:
        pass
else:
    if os.path.exists(backup_dir):
        q = input('Destination dir exists already, shall we delete it? (y/n) ')
        if not q == 'y':
            sys.exit('Ok, bye.')
        else:
            try:
                shutil.rmtree(backup_dir)
            except:
                sys.exit("Couldn't remove directory")

# list docs
listUrl = "https://api.dropboxapi.com/2/paper/docs/list"
listCont = "https://api.dropboxapi.com/2/paper/docs/list/continue"
listHeaders = {'Authorization': 'Bearer '+apikey,
                'Content-Type': 'application/json'}
listData = {'limit': 100}
listReq = requests.post(listUrl, headers=listHeaders, json=listData)

if listReq.status_code == 200:
    docs = json.loads(listReq.text)
else:
    sys.exit('error %s' % (listReq.status_code))

cursor = {'cursor': docs['cursor']['value']}

docList = docs['doc_ids']

if docs['has_more'] == True:
    cursorTrue = True
    while cursorTrue:
        if docs['has_more'] == True:
            listReq = requests.post(listCont, headers=listHeaders, json=cursor)
            if listReq.status_code == 200:
                docs = json.loads(listReq.text)
                cursor = {'cursor': docs['cursor']['value']}
                docList.extend(docs['doc_ids'])
            else:
                sys.exit('error %s' % (listReq.status_code))
        else:
            cursorTrue = False
else:
    docList = docs['doc_ids']

# get folder structure
folderList = []
folderUrl = 'https://api.dropboxapi.com/2/paper/docs/get_folder_info'
for doc in docList:
    folderData = {'doc_id': doc}
    folderReq = requests.post(folderUrl, headers=listHeaders, json = folderData)

    if folderReq.status_code == 200:
        folderInfo = json.loads(folderReq.text)
    else:
        sys.exit('error %s' % (listReq.status_code))

    if folderInfo:
        if len(folderInfo['folders']) > 1:
            tree = []
            for folder in folderInfo['folders']:
                tree.append(folder['name'])
            folderList.append({'docid': doc, 'folderName': '/'.join(tree)})
        else:
            folderList.append({'docid': doc, 'folderName': folderInfo['folders'][0]['name']})
    else:
        folderList.append({'docid': doc, 'folderName': 'root'})

# download / export
try:
    os.makedirs(os.path.normpath(backup_dir), exist_ok=True)
except:
    sys.exit("Couldn't create backup folder")

url = 'https://api.dropboxapi.com/2/paper/docs/download'
for f in folderList:
    headers = {'Authorization': 'Bearer '+apikey,
        'Dropbox-API-Arg': json.dumps({'doc_id': f['docid'], 'export_format': 'markdown'})}
    req = requests.post(url, headers=headers)

    if req.status_code == 200:
        getTitle = json.loads(req.headers['Dropbox-Api-Result'])
    else:
        sys.exit('error %s' % (listReq.status_code))

    filename = getTitle['title']+'.md'
    foldername = f['folderName']
    try:
        if foldername == 'root':
            combined = backup_dir
        else:
            os.makedirs(os.path.normpath(backup_dir)+os.sep+os.path.normpath(foldername), exist_ok=True)
            combined = os.path.normpath(backup_dir+os.sep+foldername+os.sep)
        writefile = open(os.path.join(combined, filename), 'w')
        writefile.write(req.text)
        writefile.close()
        print('saved "%s" to "%s"' % (filename, combined))
    except:
        sys.exit("Couldn't write file.")
