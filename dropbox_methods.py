import dropbox
import login_data
import config
import os
from merge_databases import sync
import time


def download_db(download_as=config.db_path):
    dbx = dropbox.Dropbox(login_data.dropbox_access_token)
    print("Downloading database..")
    dbx.files_download_to_file(path=f'/{config.db_path}', download_path=f'./{download_as}')
    while not os.path.exists(download_as):
        time.sleep(1)
    print("Download finished.")


def upload_db(file_name=config.db_path):
    dbx = dropbox.Dropbox(login_data.dropbox_access_token)
    print("Uploading database..")
    with open(file_name, 'rb') as f:
        dbx.files_upload(f.read(), f'/{file_name}', mode=dropbox.files.WriteMode.overwrite)
    print("Upload finished.")


def merge_and_upload():
    download_db(config.db_path)
    sync(config.local_db_path, config.db_path)
    upload_db(config.db_path)


if __name__ == "__main__":
    choice = 0
    while choice != 'u' and choice != 'd':
        choice = input("Do you wish to upload or download the database?(upload - u, download - d)\n:")

    if choice == 'u':
        upload_db()
    else:
        download_db()
