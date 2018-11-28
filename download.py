from __future__ import print_function
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from httplib2 import Http
from oauth2client import file, client, tools
from os import makedirs
from os.path import dirname, exists

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/drive.readonly'

def main():
    # if there is no token.json then use credentials.json to make token.json
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)

    # initialize drive api v3
    service = build('drive', 'v3', http=creds.authorize(Http()))

    # next page token check: if page token is exists then start from that page
    next_page_token_sign = False
    next_page_token = ""
    if exists("next_page_token.txt"):
        next_page_token_sign = True
        with open("next_page_token.txt", "r") as f:
            next_page_token = f.read()

    # make directory to save downloaded images
    if not exists("images"):
        makedirs("images")

    while(True):
        if next_page_token_sign:
            print("next_page_token:" + next_page_token)
            results = service.files().list(
                pageToken=next_page_token,
                q="mimeType contains 'image/'",
                pageSize=100,
                orderBy="createdTime",
                fields="nextPageToken, files(id, name, mimeType)").execute()

            next_page_token = results.get('nextPageToken')
            save_token(next_page_token)

            items = results.get('files', [])
            if not items:
                print('No files found.')
                break
            else:
                for item in items:
                    print(u'{0}: {1} {2}'.format(item['id'], item['name'], item['mimeType']))
                    save_file(service, item['id'], item['mimeType'].split("/")[1])
        else:
            results = service.files().list(
                q="mimeType contains 'image/'",
                pageSize=100,
                orderBy="createdTime",
                fields="nextPageToken, files(id, name, mimeType)").execute()

            next_page_token = results.get('nextPageToken')
            next_page_token_sign = True
            save_token(next_page_token)

            items = results.get('files', [])
            if not items:
                print('No files found.')
                break
            else:
                for item in items:
                    print(u'{0}: {1} {2}'.format(item['id'], item['name'], item['mimeType']))
                    save_file(service, item['id'], item['mimeType'].split("/")[1])


def save_token(next_page_token):
    with open("next_page_token.txt", "w") as f:
        f.write(next_page_token)


def save_file(service, file_id, extention):
    request = service.files().get_media(fileId=file_id)
    with open(u"images/{0}.{1}".format(file_id, extention), "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))

if __name__ == '__main__':
    main()
