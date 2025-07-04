import os,io
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaIoBaseDownload
import fitz  # PyMuPDF
from langchain.schema import Document
from app.helpers.helpers import load_cache,compute_hash,extract_category_from_filename,save_cache

# === DRIVE CONFIG ===
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
FOLDER_NAME = "BMVSI_HR_POLICIES"

# === DocumentLoader ===
class DocumentLoader:

    def _get_drive_service(self):
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Force full re-consent every time to get a refresh_token
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(
                    port=8080,
                    access_type='offline',   # <- Ensures refresh_token is returned
                    prompt='consent'         # <- Forces re-consent
                )

            # Save new token with refresh_token
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        return build("drive", "v3", credentials=creds)

    def _load_documents(self):
        service = self._get_drive_service()
        cache_path = "documents_cache/drive_index.json"
        cache = load_cache(cache_path)

        folder_query = f"name = '{FOLDER_NAME}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        folder_id = service.files().list(q=folder_query, fields="files(id)").execute()["files"][0]["id"]

        pdf_query = f"'{folder_id}' in parents and mimeType = 'application/pdf' and trashed = false"
        files = service.files().list(q=pdf_query, fields="files(id, name, modifiedTime)").execute()["files"]

        docs = []
        updated_cache = {}

        for file in files:
            file_id = file["id"]
            file_name = file["name"]
            modified_time = file["modifiedTime"]

            cached = cache.get(file_name)
            if cached and cached["modified_time"] == modified_time:
                updated_cache[file_name] = cached
                continue

            request = service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            MediaIoBaseDownload(fh, request).next_chunk()
            fh.seek(0)
            file_bytes = fh.read()
            content_hash = compute_hash(file_bytes)

            if cached and cached["hash"] == content_hash:
                updated_cache[file_name] = cached
                continue

            pdf = fitz.open(stream=file_bytes, filetype="pdf")
            full_text = "".join(page.get_text() for page in pdf)

            category = extract_category_from_filename(file_name)
            print('category:- ',category)
            docs.append(Document(page_content=full_text, metadata={"source": file_name, "category": category}))

            updated_cache[file_name] = {
                "file_id": file_id,
                "modified_time": modified_time,
                "hash": content_hash
            }

        save_cache(updated_cache, cache_path)
        return docs
