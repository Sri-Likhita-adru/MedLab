from dropbox_client import DropboxClient

dbx = DropboxClient()

# Upload entire DS5 folder
local_folder = "/data/sri_1/Desktop/DS5"
dropbox_folder = "/MedLab_Artery/DS5"  # Dropbox target path
dbx.upload_folder(local_folder, dropbox_folder)
