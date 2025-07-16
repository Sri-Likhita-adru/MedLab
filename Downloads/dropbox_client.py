### File: dropbox_client.py
import os
import dropbox

class DropboxClient:
    """
    Supports short lived tokens + auto refresh via DROPBOX_REFRESH_TOKEN,
    or legacy long lived token via DROPBOX_TOKEN.
    """
    def __init__(self):
        # Try refresh‐token flow first
        app_key       = os.environ.get("DROPBOX_APP_KEY")
        app_secret    = os.environ.get("DROPBOX_APP_SECRET")
        refresh_token = os.environ.get("DROPBOX_REFRESH_TOKEN")

        if app_key and app_secret and refresh_token:
            # SDK will auto‐refresh expired access tokens for you
            self.dbx = dropbox.Dropbox(
                app_key=app_key,
                app_secret=app_secret,
                oauth2_refresh_token=refresh_token
            )
        else:
            # Fallback to legacy long‐lived token
            token = os.environ.get("DROPBOX_TOKEN")
            if not token:
                raise ValueError(
                    "Must set either DROPBOX_REFRESH_TOKEN (with APP_KEY/SECRET) "
                    "or DROPBOX_TOKEN"
                )
            self.dbx = dropbox.Dropbox(token)

    def download(self, dropbox_path: str, local_path: str, overwrite: bool = True):
        """
        Download a file from Dropbox to a local path.
        If overwrite is True, will replace the local file if it exists.
        """
        if os.path.exists(local_path) and not overwrite:
            return local_path
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        metadata, res = self.dbx.files_download(dropbox_path)
        with open(local_path, "wb") as f:
            f.write(res.content)
        print(f"Downloaded '{dropbox_path}' to '{local_path}'")
        return local_path

    def upload(self, local_path: str, dropbox_path: str, overwrite: bool = True):
        """
        Upload a local file to Dropbox.
        If overwrite is True, will replace the remote file if it exists.
        """
        mode = dropbox.files.WriteMode.overwrite if overwrite else dropbox.files.WriteMode.add
        with open(local_path, "rb") as f:
            data = f.read()
        self.dbx.files_upload(data, dropbox_path, mode=mode)
        print(f"Uploaded '{local_path}' to '{dropbox_path}'")
        return dropbox_path
    
    def create_folder(self, dropbox_folder: str):
        """
        Create a folder on Dropbox; ignore if it already exists.
        """
        try:
            self.dbx.files_create_folder_v2(dropbox_folder)
        except Exception:
            pass

    def upload_file(self, local_path: str, dropbox_path: str, overwrite: bool = True):
        """
        Alias for upload(), for backwards compatibility.
        """
        return self.upload(local_path, dropbox_path, overwrite)

    def upload_folder(self, local_folder: str, dropbox_folder: str):
        """
        Recursively upload a local folder to Dropbox.
        """
        for root, dirs, files in os.walk(local_folder):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, local_folder)
                dropbox_path_full = os.path.join(dropbox_folder, relative_path).replace("\\", "/")
                self.upload(local_path, dropbox_path_full)
