# RAG Website

## Purpose

A **Flask web application** for managing Azure AI Search RAG indexes.
It lets you create, edit, and delete indexes, and populate them by
uploading **PDFs** or **scraping websites**.

- **Web UI:** `http://10.55.55.1:7000`

## What it does

### Routes

| Route | Method | Description |
|---|---|---|
| `/` | GET | Lists all indexes with name, doc count, description, created date |
| `/show_create_index` | GET | Shows the create-index form |
| `/create_index` | POST | Creates a new index; uploads PDFs and/or scrapes a URL |
| `/edit_index_page` | POST | Shows the edit form for an existing index |
| `/edit_index` | POST | Adds PDFs/URLs to an existing index; updates description |
| `/delete_index` | POST | Deletes an index from Azure Search |
| `/process_selected_links` | POST | Starts a background scraping job for a list of URLs |
| `/status/<task_id>` | GET | Returns JSON progress for a background scraping job |

### Website scraping flow

1. User submits a URL when creating or editing an index.
2. Server fetches the page with **trafilatura** (clean text) and **lxml** (same-domain links).
3. If links are found, user is shown a checkbox selection page.
4. Selected links are scraped in a **background thread**; progress bar polls `/status/<task_id>`.

### Document schema in Azure Search

| Field | Type | Key | Description |
|---|---|---|---|
| `id` | String | Yes | `doc-<uuid>-<n>` (PDF) or `url-chunk-<uuid>-<n>` (web) |
| `content` | String | No | The text chunk |
| `page` | Int32 | No | Page number (PDF) or `1` (web) |
| `contentVector` | Collection(Single) | No | Embedding vector |

### Local metadata

`config/index_info.json` stores index metadata (description, created date, status)
alongside what Azure Search tracks.


## Environment variables

| Variable | Used for |
|---|---|
| `AZURE_SEARCH_KEY` | Azure AI Search API key |
| `AZURE_LLM_API_KEY_ARIZONA` | Azure OpenAI embedding API key |
| `AZURE_LLM_API_KEY_VIRGINIA` | Azure OpenAI embedding API key |

## Steps:

1. Make an text-embedding model [text-embedding model](azure-ai-foundry.md#step-3-deploy-an-ai-model)
2. Make files and paste in the corresponding blocks of code below

    * Search API key can be found by going into that resource, open up Settings on the left side meny, then go into keys.


## systemd Unit

`/etc/systemd/system/rag-website.service`

```ini
[Unit]
Description=RAG Website (Flask)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=<VM_user_name> # will need to update this to the chosen user name when the VM was created
WorkingDirectory=/home/<VM_user_name>/rag-website # update with user name
ExecStart=/home/<VM_user_name>/rag-website/.venv/bin/python /home/<VM_user_name>/rag-website/server.py --host 10.55.55.1 --port 7000 # update with user name
Restart=on-failure
RestartSec=2
Environment=AZURE_SEARCH_KEY=your-search-key-here # update with key
Environment=AZURE_LLM_API_KEY_ARIZONA=your-openai-key-here # update with key

[Install]
WantedBy=multi-user.target
```

### Install and start

```bash
mkdir -p ~/rag-website
cd ~/rag-website
# Put all of the files into this folder

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

sudo nano /etc/systemd/system/rag-website.service
# Paste the unit above, fill in the real key values

sudo systemctl daemon-reload
sudo systemctl enable --now rag-website

# Check it's running
sudo systemctl status rag-website

# Follow logs
sudo journalctl -u rag-website -f
```

The UI will be at `http://10.55.55.1:7000`.

---

## Files

### `requirements.txt`

```txt
Flask==3.1.2
openai==2.16.0
azure-search-documents==11.6.0
tiktoken==0.12.0
pypdf==6.6.2
PyYAML==6.0.3
trafilatura==2.0.0
lxml==6.0.2
pydantic==2.12.5
```

### `config/config.yaml`

```yaml
search_config:
  endpoint: "https://chris-rag-testing.search.azure.us"
  api_key: AZURE_SEARCH_KEY

embedding:
  endpoint: "https://ai-aifoundryarizona750873844815.openai.azure.us/openai/deployments/text-embedding-3-large/embeddings?api-version=2023-05-15"
  api_key: AZURE_LLM_API_KEY_ARIZONA
  api_version: "2024-02-01"
  model: "text-embedding-3-large"
```

### `server.py`

```python
from src.azure_client import AzureClient
from flask import Flask, request, jsonify, render_template
from src.schemas import IndexList, IndexInfo
import argparse
import datetime
import logging
import threading
import uuid




class Server:
    def __init__(self, config_path):
        self.azure_client = AzureClient(config_path)
        self.index_info_list = IndexList()

        self.app  = Flask(__name__)
        self.add_route("/", self.load_page)
        self.add_route("/delete_index", self.delete_index)
        self.add_route("/create_index", self.create_index)
        self.add_route("/show_create_index", self.show_create_index)
        self.add_route("/edit_index_page", self.edit_index_page)
        self.add_route("/edit_index", self.edit_index)
        self.add_route("/process_selected_links", self.handle_selected_links)        
        self.job_progress = {} # shared tracker for background jobs
        self.app.add_url_rule("/status/<task_id>", view_func=self.get_status, methods=['GET'])
   

    def _return_message(self, message, success=True):
        if success:
            return render_template("success_message.html", message=message)
        else:
            return render_template("failure_message.html", message=message)

    def create_index(self):
        form_data = request.form
        index_name = form_data.get('name')
        search_dim = int(form_data.get('dimensions', 3072))
        chunk_size = int(form_data.get('chunk_size', 800))
        description = form_data.get('description', 'None provided')
        uploaded_files = request.files.getlist('files')
        uploaded_url = request.form.get('url')

        if not index_name:
            return jsonify({"error": "Index name is required"}), 400
        try:
            self.azure_client.create_index(index_name, search_dim=search_dim)
            for file in uploaded_files:
                if file.filename.endswith('.pdf'):
                    self.azure_client.upload_pdf(file, index_name, chunk_size=chunk_size)
            if uploaded_url:
                extracted_text, links = self.azure_client.process_url_and_find_links(uploaded_url)
                # Upload the base text
                if extracted_text:
                    self.azure_client.upload_text(extracted_text, index_name, chunk_size=chunk_size)
                # If we found links, intercept the JSON response and send them to the HTML page instead!
                if links:
                    return render_template('select_links.html', links=links, current_url=uploaded_url, index_name=index_name)     
      
            index_info = IndexInfo(
                name=index_name,
                dimensions=search_dim,
                created_at=datetime.datetime.now().isoformat(timespec='minutes'),
                description=description[:100], # Limit description to 100 chars for display
                status='active'
            )
            self.index_info_list.save_index_info(index_info)
            return self._return_message(f"Index '{index_name}' created and files uploaded successfully")
        except Exception as e:
            logging.error(f"Error creating index: {e}")
            return self._return_message(f"Error creating index: {e}", success=False)
        
    def edit_index(self):
        form_data = request.form
        index_name = form_data.get('name')
        description = form_data.get('description', 'None provided')
        files = request.files.getlist('files')
        uploaded_url = form_data.get('url')
        chunk_size = int(form_data.get('chunk_size', 800))

        if not index_name:
            return jsonify({"error": "Index name is required"}), 400

        try:
            self.index_info_list.update_index_info(index_name, description=description)
            for file in files:                
                if file.filename.endswith('.pdf'):
                    self.azure_client.upload_pdf(file, index_name, chunk_size=chunk_size)
            if uploaded_url:
                extracted_text, links = self.azure_client.process_url_and_find_links(uploaded_url)
                if extracted_text:
                    self.azure_client.upload_text(extracted_text, index_name, chunk_size=chunk_size)
                if links:
                    return render_template('select_links.html', links=links, current_url=uploaded_url, index_name=index_name)
            return self._return_message(f"Index '{index_name}' updated successfully")
        except Exception as e:
            logging.error(f"Error editing index: {e}")
            return self._return_message(f"Error editing index: {e}", success=False)

    def edit_index_page(self):
        index_name = request.form.get("index_name")
        if not index_name:
            return self._return_message("Index name is required to edit", success=False)
        info = self.index_info_list.get_index_info(index_name)
        if info is None:
            info = IndexInfo(name=index_name, dimensions=0, created_at="N/A", description="No description provided", status="unknown")
        names = self.azure_client.get_index_names()
        for idx in names:
            if idx['name'] == index_name:
                info.documents = idx.get('document_count')
                break
        return render_template("edit_index.html", index=info)
        

    def show_create_index(self):
        return render_template("create_index.html")

    def load_page(self):
        indexes: list[dict] = self.azure_client.get_index_names()
        for idx in indexes:
            idx.setdefault("created_at", "N/A")
            idx.setdefault("status", "active")
            idx.setdefault("description", "No description provided")
            info = self.index_info_list.get_index_info(idx['name'])
            if info is not None:
                idx["created_at"] = info.created_at
                idx["status"] = info.status
                idx["description"] = info.description
        return render_template("index.html", indexes=indexes)
    
    def delete_index(self):
        index_name = request.form.get("index_name")
        if not index_name:
            return jsonify({"error": "Index name is required"}), 400
        
        try:
            self.azure_client.delete_index(index_name)
            self.index_info_list.delete_index_info(index_name)
            return self._return_message(f"Index '{index_name}' deleted successfully")
        except Exception as e:
            logging.error(f"Error deleting index: {e}")
            return self._return_message(f"Error deleting index: {e}", success=False)
        
    def handle_selected_links(self):
        selected_urls = request.form.getlist('selected_links')
        index_name = request.form.get('index_name', 'my-index') # Fallback if missing

        if not selected_urls:
            return "No links selected."

        task_id = str(uuid.uuid4())

        # Start the background thread
        thread = threading.Thread(
            target=self.background_scraping_job, 
            args=(task_id, selected_urls, index_name)
        )
        thread.start()
        # Immediately load the progress bar
        return render_template('download_progress.html', task_id=task_id)
    
    def get_status(self, task_id):
        data = self.job_progress.get(task_id, {"status": "unknown"})
        return jsonify(data)

    def background_scraping_job(self, task_id, url_list, index_name):
        total_urls = len(url_list)
        # Initialize the job on the bulletin board
        self.job_progress[task_id] = {"total": total_urls, "completed": 0, "status": "running"}

        for i, url in enumerate(url_list):
            try:
                print(f"Processing: {url}")
                extracted_text, _ = self.azure_client.process_url_and_find_links(url)
                if extracted_text:
                    self.azure_client.upload_text(extracted_text, index_name)
            except Exception as e:
                print(f"Error on {url}: {e}")
            
            # Update the board after finishing a URL
            self.job_progress[task_id]["completed"] = i + 1

        # Mark as finished when the loop exits
        self.job_progress[task_id]["status"] = "completed"


    def add_route(self, route, handler):
        self.app.add_url_rule(route, view_func=handler, methods=['POST', 'GET'])

    def start(self, host="127.0.0.1", port=5000):
        self.app.run(host=host, port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    server = Server(config_path="config/config.yaml")
    server.start(host=args.host, port=args.port)
```

### `src/azure_client.py`

```python
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from openai import AzureOpenAI
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
)

import tiktoken
from pypdf import PdfReader
import logging
import os
import uuid
import yaml
# for website scraping
import trafilatura
from lxml import html
from urllib.parse import urlparse

# The schema for our search index
def create_index_schema(search_dim=3072):
    return [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SimpleField(name="page", type=SearchFieldDataType.Int32),
            SearchField(
                name="contentVector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                vector_search_dimensions=search_dim,
                vector_search_profile_name="vec-profile",
            ),
        ]

class ModelWrapper:
    """
    Wrapper class to create Azure OpenAI models from YAML configuration dicts
    """
    def __init__(self, config_dict: dict):
        self.api_key = os.getenv(config_dict.get("api_key"))
        self.endpoint = config_dict.get("endpoint")
        self.api_version = config_dict.get("api_version")

        self.model = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version=self.api_version
        )

    def get_model(self):
        return self.model


class AzureClient:
    def __init__(self, config_path):

        # Load the YAML configuration values
        self._load_config(config_path)

        # Initialize Azure Search clients
        # This is what is used to search our RAG database
        self.index_client = SearchIndexClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.api_key)
        )

        self.logger = logging.getLogger(__name__)
        self.logger.level = logging.DEBUG

        self.embeddings_model = ModelWrapper(self.embedding_config).get_model()
        self.embedding_name = self.embedding_config.get("model")

    def _load_config(self, path):
        """
        Open a YAML file and parse for the necessary information on endpoints and 
        API keys"""
        config: dict = yaml.load(open(path, 'r'), Loader=yaml.FullLoader)
        assert config is not None, "Config file is empty or invalid"

        self.endpoint = config.get("search_config", {}).get("endpoint", None)
        api_key_env = config.get("search_config", {}).get("api_key", None)
        self.api_key = os.getenv(api_key_env) if api_key_env else None

        self.embedding_config = config.get("embedding", {})

        if not self.endpoint:
            raise ValueError("Missing search_config.endpoint in config.yaml")
        if not self.api_key:
            raise ValueError(f"Environment variable '{api_key_env}' is not set")
        if not self.embedding_config:
            raise ValueError("Missing embedding section in config.yaml")


    def _index_exists(self, index_name):
        """
        Check if an index exists within the Azure database
        """
        existing = self.index_client.list_index_names()
        return index_name in existing

    def get_index_names(self):
        """
        Returns a list of dictionaries containing index details
        """
        indexes = []
        for name in self.index_client.list_index_names():
            stats = self.index_client.get_index_statistics(name)
            indexes.append({
                "name": name,
                "id": name,
                "document_count": stats['document_count'],
            })
        return indexes

    def _get_search_client(self, index_name):
        """
        Returns a SearchClient for the specified index
        """
        return SearchClient(
            endpoint=self.endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(self.api_key)
        )
       
    def create_index(self, index_name, search_dim=3072):
        """
        Creates a new RAG index with the specified name.
        If the index already exists, it will be deleted and recreated.
        """
        try:
            self.index_client.delete_index(index_name)
        except:
            pass

        algorithm = HnswAlgorithmConfiguration(
            name='vec-config',
        )

        vector_search = VectorSearch(
            algorithms=[algorithm],
            profiles=[
                VectorSearchProfile(
                    name="vec-profile",
                    algorithm_configuration_name="vec-config"
                )
            ]
        )

        index = SearchIndex(
            name=index_name,
            fields=create_index_schema(search_dim),
            vector_search=vector_search
        )

        self.index_client.create_index(index)
        self.logger.info(f"Created index: {index_name}")

    def _chunk_pdf(self, doc, chunk_size=800):
        enc = tiktoken.get_encoding("cl100k_base")


        def chunk_text(text, max_tokens=chunk_size):
            tokens = enc.encode(text)
            chunks = []
            for i in range(0, len(tokens), max_tokens):
                chunk_tokens = tokens[i:i + max_tokens]
                chunk_text = enc.decode(chunk_tokens)
                chunks.append(chunk_text)
            return chunks

        reader = PdfReader(doc)
        all_chunks = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            chunks = chunk_text(text)
            for c in chunks:
                all_chunks.append((i + 1, c))

        self.logger.info(f"Extracted {len(all_chunks)} chunks from PDF")
        return all_chunks
    
    def _embed_text(self, text):
        response = self.embeddings_model.embeddings.create(
            model=self.embedding_name,
            input=text
        )

        return response.data[0].embedding
            

    def upload_pdf(self, pdf, index_name, chunk_size=800, upload_freq=50):
        """
        Uploads a PDF to the specified index.
        Creates the index if it doesn't exist.
        """
        # Create index if it doesn't exist
        if not self._index_exists(index_name):
            self.create_index(index_name)

        self.logger.info(f"Beginning PDF upload to index '{index_name}', please wait...")
        chunks = self._chunk_pdf(pdf, chunk_size=chunk_size)

        search_client = self._get_search_client(index_name)
        batch_id = str(uuid.uuid4())

        batch = []
        for i, (page, text) in enumerate(chunks):
            emb = self._embed_text(text)
            doc = {
                "id": f"doc-{batch_id}-{i}",
                "content": text,
                "page": page,
                "contentVector": emb
            }
            batch.append(doc)

            if len(batch) >= upload_freq:
                search_client.upload_documents(documents=batch)
                batch.clear()
        
        if batch:
            search_client.upload_documents(documents=batch)

        self.logger.info(f"All PDF chunks uploaded to index '{index_name}'")

    def query_db(self, query, index_name, k=5):
        """
        Queries the specified index for relevant content.
        """
        if not self._index_exists(index_name):
            raise ValueError(f"Index '{index_name}' does not exist")

        query_emb = self._embed_text(query)
        search_client = self._get_search_client(index_name)

        results = search_client.search(
            search_text=None,
            vectors=[
                {
                    "value": query_emb,
                    "fields": "contentVector",
                    "k": k
                }
            ]
        )
        text_chunks = []
        for r in results:
            text_chunks.append(r['content'])
        return text_chunks

    def upload_text(self, text, index_name, chunk_size=800, upload_freq=50):
        if not text or len(text) < 10:
            print("❌ ERROR: Text content is empty or too short!")
            return False

        print(f"✅ Text found: {len(text)} characters. Proceeding...")

        if not self._index_exists(index_name):
            print(f"ℹ️ Creating new index '{index_name}'...")
            self.create_index(index_name)

        enc = tiktoken.get_encoding("cl100k_base")
        tokens = enc.encode(text)
        print(f"📊 Token count: {len(tokens)}")

        chunks = []
        for i in range(0, len(tokens), chunk_size):
            chunk_tokens = tokens[i:i + chunk_size]
            chunks.append(enc.decode(chunk_tokens))
        
        print(f"✂️ Total chunks created: {len(chunks)}")

        search_client = self._get_search_client(index_name)
        batch_id = str(uuid.uuid4())
        batch = []

        for i, chunk_content in enumerate(chunks):
            try:
                emb = self._embed_text(chunk_content)

                if i == 0:
                    print(f"📏 Embedding Dimension Detected: {len(emb)}")

                doc = {
                    "id": f"url-chunk-{batch_id}-{i}",
                    "content": chunk_content,
                    "page": 1, 
                    "contentVector": emb
                }
                batch.append(doc)

                if len(batch) >= upload_freq:
                    print(f"✅   Uploading batch of {len(batch)}...")
                    search_client.upload_documents(documents=batch)
                    batch.clear()
                    
            except Exception as e:
                print(f"❌ CRITICAL ERROR on chunk {i}: {str(e)}")
                break 

        if batch:
            print(f"   Uploading final batch of {len(batch)}...")
            try:
                search_client.upload_documents(documents=batch)
                print("✅ Final batch uploaded successfully!")
            except Exception as e:
                print(f"❌ CRITICAL ERROR on final batch: {str(e)}")

        print(f"🏁 Finished processing.")
        return True

    def process_url_and_find_links(self, current_url):
        print(f"\n--- Processing: {current_url} ---")
        
        downloaded = trafilatura.fetch_url(current_url)
        
        if downloaded is None:
            print(f"❌ Failed to download {current_url}")
            return None, []

        main_text = trafilatura.extract(downloaded, include_comments=False, include_tables=True)

        tree = html.fromstring(downloaded)
        tree.make_links_absolute(current_url)
        raw_links = tree.xpath('//a')
        
        viable_links = []
        seen_urls = set()
        base_domain = urlparse(current_url).netloc

        for link in raw_links:
            href = link.get('href')
            text = link.text_content().strip()
            
            if not href: continue
            if href.startswith(('mailto:', 'javascript:', '#')): continue
            if urlparse(href).netloc != base_domain:
                continue
            if href not in seen_urls and len(text) > 0:
                seen_urls.add(href)
                viable_links.append({'text': text, 'url': href})

        return main_text, viable_links

    def search_url_loop(self, uploaded_url, index_name, chunk_size=800, upload_freq=50):
        start_url = uploaded_url
        queue = [start_url]
        visited = set()

        while queue:
            current_url = queue.pop(0)
            
            if current_url in visited:
                continue
                
            visited.add(current_url)

            extracted_text, links = self.process_url_and_find_links(current_url)
            
            if extracted_text:
                print(f"Pushing {current_url} content to Azure...")
                self.upload_text(extracted_text, index_name, chunk_size=chunk_size, upload_freq=upload_freq)
            else:
                print(f"No usable text found on {current_url}.")

            if not links:
                print("No viable links found.")
                continue

            print(f"\nFound {len(links)} links on {current_url}:")
            for i, link in enumerate(links):
                print(f"[{i}] {link['text'][:50]}... -> {link['url']}")

            print("\nWhich links to add to the queue?")
            print("Type numbers (e.g., '1, 5, 10'), 'all', or press Enter to skip.")
            
            selection = input("Selection > ").strip().lower()

            if selection == 'all':
                for link in links:
                    if link['url'] not in visited:
                        queue.append(link['url'])
                print(f"Added {len(links)} links to queue.")
                
            elif selection:
                try:
                    indices = [int(x.strip()) for x in selection.split(',')]
                    count = 0
                    for i in indices:
                        if 0 <= i < len(links):
                            target_url = links[i]['url']
                            if target_url not in visited and target_url not in queue:
                                queue.append(target_url)
                                count += 1
                    print(f"Added {count} links to queue.")
                except ValueError:
                    print("Invalid input. Moving on...")


    def delete_index(self, index_name):
        """
        Deletes the specified index from the Azure Search service.
        """
        if not self._index_exists(index_name):
            raise ValueError(f"Index '{index_name}' does not exist")

        self.index_client.delete_index(index_name)
        self.logger.info(f"Deleted index: {index_name}")
```

### `src/schemas.py`

```python
from pydantic import BaseModel
from typing import Optional
import json
import os

INFO_PATH = "config/index_info.json"


class IndexInfo(BaseModel):
    name: str
    dimensions: int
    created_at: str
    description: str
    status: str
    documents: Optional[int] = None


class IndexList:
    def __init__(self):
        self.indexes: list[IndexInfo] = []
        self.load_indexes()
        
    def load_indexes(self):
        try:
            with open(INFO_PATH, "r") as f:
                data = json.load(f)
                self.indexes = [IndexInfo(**idx) for idx in data.get("indexes", [])]
        except FileNotFoundError:
            os.makedirs(os.path.dirname(INFO_PATH), exist_ok=True)
            with open(INFO_PATH, "w") as f:
                json.dump({"indexes": []}, f)
            self.indexes = []


    def get_index_info(self, index_name) -> IndexInfo | None:
        for idx in self.indexes:
            if idx.name == index_name:
                return idx
        return None
    
    def save_index_info(self, index_info: IndexInfo):
        existing = self.get_index_info(index_info.name)
        if existing:
            self.indexes = [idx if idx.name != index_info.name else index_info for idx in self.indexes]
        else:
            self.indexes.append(index_info)
        with open(INFO_PATH, "w") as f:
            json.dump({"indexes": [idx.model_dump() for idx in self.indexes]}, f, indent=4)


    def delete_index_info(self, index_name):
        self.indexes = [idx for idx in self.indexes if idx.name != index_name]
        with open(INFO_PATH, "w") as f:
            json.dump({"indexes": [idx.model_dump() for idx in self.indexes]}, f, indent=4)

    def update_index_info(self, index_name, description=None):
        idx = self.get_index_info(index_name)
        if idx:
            if description is not None:
                idx.description = description[:100]  # Limit description to 100 chars
            self.save_index_info(idx)
        else:
            new_idx = IndexInfo(
                name=index_name,
                dimensions=0,
                created_at="N/A",
                description=description[:100] if description else "No description provided",
                status="active"
            )
            self.save_index_info(new_idx)
```

### `templates/index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Index Manager</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 40px 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        header { text-align: center; margin-bottom: 40px; }
        h1 { color: #fff; font-size: 2.5rem; font-weight: 600; text-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .subtitle { color: rgba(255,255,255,0.8); margin-top: 10px; font-size: 1.1rem; }
        .card { background: #fff; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.15); overflow: hidden; }
        .card-header { background: #f8f9fa; padding: 20px 30px; border-bottom: 1px solid #e9ecef; display: flex; justify-content: space-between; align-items: center; }
        .card-header h2 { color: #333; font-size: 1.3rem; font-weight: 600; }
        .btn { display: inline-flex; align-items: center; gap: 8px; padding: 10px 20px; border: none; border-radius: 8px; font-size: 0.9rem; font-weight: 500; cursor: pointer; transition: all 0.2s ease; text-decoration: none; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(102,126,234,0.4); }
        .btn-warning { background: #ffc107; color: #333; }
        .btn-warning:hover { background: #e0a800; }
        .btn-danger { background: #dc3545; color: #fff; }
        .btn-danger:hover { background: #c82333; }
        .btn-sm { padding: 6px 12px; font-size: 0.8rem; }
        .table-container { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; }
        thead { background: #f8f9fa; }
        th { padding: 16px 20px; text-align: left; font-weight: 600; color: #495057; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #e9ecef; }
        td { padding: 16px 20px; color: #333; border-bottom: 1px solid #e9ecef; vertical-align: middle; }
        tbody tr:hover { background: #f8f9fa; }
        .status-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 500; }
        .status-active { background: #d4edda; color: #155724; }
        .status-inactive { background: #f8d7da; color: #721c24; }
        .status-pending { background: #fff3cd; color: #856404; }
        .action-buttons { display: flex; gap: 8px; flex-wrap: wrap; }
        .empty-state { text-align: center; padding: 60px 20px; color: #6c757d; }
        .search-box { display: flex; gap: 10px; }
        .search-input { padding: 10px 16px; border: 1px solid #ddd; border-radius: 8px; font-size: 0.9rem; width: 250px; }
        .search-input:focus { outline: none; border-color: #667eea; }
        .index-name { font-weight: 600; color: #667eea; }
        footer { text-align: center; margin-top: 40px; color: rgba(255,255,255,0.7); font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Index Manager</h1>
            <p class="subtitle">RDA management of RAG indexes</p>
        </header>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="flash-messages">
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}

        <div class="card">
            <div class="card-header">
                <h2>All Indexes</h2>
                <div class="search-box">
                    <input type="text" class="search-input" id="searchInput" placeholder="Search indexes..." onkeyup="filterTable()">
                    <a href="{{ url_for('show_create_index') }}" class="btn btn-primary">
                        <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
                        </svg>
                        Create Index
                    </a>
                </div>
            </div>
            <div class="table-container">
                {% if indexes %}
                <table id="indexTable">
                    <thead>
                        <tr>
                            <th>#</th><th>Index Name</th><th>Description</th><th>Documents</th><th>Status</th><th>Created</th><th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for index in indexes %}
                        <tr>
                            <td>{{ loop.index }}</td>
                            <td class="index-name">{{ index.name }}</td>
                            <td>{{ index.description or 'No description' }}</td>
                            <td>{{ index.document_count }}</td>
                            <td>
                                {% if index.status == 'active' %}<span class="status-badge status-active">Active</span>
                                {% elif index.status == 'inactive' %}<span class="status-badge status-inactive">Inactive</span>
                                {% else %}<span class="status-badge status-pending">Pending</span>{% endif %}
                            </td>
                            <td>{{ index.created_at }}</td>
                            <td>
                                <div class="action-buttons">
                                    <form action="/edit_index_page" method="POST" style="display:inline;">
                                        <input type="hidden" name="index_name" value="{{ index.name }}">
                                        <button type="submit" class="btn btn-warning btn-sm">Edit</button>
                                    </form>
                                    <form action="/delete_index" method="POST" style="display:inline;" onsubmit="return confirm('Are you sure you want to delete this index?');">
                                        <input type="hidden" name="index_name" value="{{ index.name }}">
                                        <button type="submit" class="btn btn-danger btn-sm">Delete</button>
                                    </form>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <div class="empty-state">
                    <h3>No Indexes Found</h3>
                    <p>Get started by creating your first index.</p>
                </div>
                {% endif %}
            </div>
        </div>
        <footer><p>&copy; 2026 Brigham Young University. All rights reserved.</p></footer>
    </div>
    <script>
        function filterTable() {
            const filter = document.getElementById('searchInput').value.toLowerCase();
            const table = document.getElementById('indexTable');
            if (!table) return;
            const rows = table.getElementsByTagName('tr');
            for (let i = 1; i < rows.length; i++) {
                const cells = rows[i].getElementsByTagName('td');
                let found = false;
                for (let j = 0; j < cells.length; j++) {
                    if (cells[j].textContent.toLowerCase().indexOf(filter) > -1) { found = true; break; }
                }
                rows[i].style.display = found ? '' : 'none';
            }
        }
    </script>
</body>
</html>
```

### `templates/create_index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create Index</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; }
        .container { background: white; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); padding: 40px; max-width: 500px; width: 100%; }
        h1 { color: #333; margin-bottom: 30px; text-align: center; font-size: 28px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; color: #555; font-weight: 600; margin-bottom: 8px; font-size: 14px; }
        .loading-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(255,255,255,0.9); display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 9999; visibility: hidden; opacity: 0; transition: visibility 0s, opacity 0.3s linear; }
        .loading-overlay.active { visibility: visible; opacity: 1; }
        .spinner { border: 5px solid #f3f3f3; border-top: 5px solid #667eea; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; margin-bottom: 15px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .loading-text { color: #333; font-size: 18px; font-weight: 500; }
        .loading-subtext { color: #666; font-size: 14px; margin-top: 5px; }
        input[type="text"], input[type="number"], select, textarea { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 5px; font-size: 14px; transition: border-color 0.3s; font-family: inherit; }
        input[type="text"]:focus, input[type="number"]:focus, select:focus, textarea:focus { outline: none; border-color: #667eea; }
        input[type="file"] { display: block; width: 100%; padding: 10px; border: 2px dashed #e0e0e0; border-radius: 5px; cursor: pointer; font-size: 14px; }
        input[type="file"]:hover { border-color: #667eea; }
        .button-group { display: flex; gap: 10px; margin-top: 30px; }
        button { flex: 1; padding: 12px; border: none; border-radius: 5px; font-size: 16px; font-weight: 600; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; }
        .submit-btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .submit-btn:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(102,126,234,0.4); }
        .back-btn { background: #f0f0f0; color: #333; }
        .back-btn:hover { background: #e0e0e0; transform: translateY(-2px); }
    </style>
</head>
<body>
    <div class="loading-overlay" id="loadingOverlay">
        <div class="spinner"></div>
        <div class="loading-text">Creating Index & Uploading Files</div>
        <div class="loading-subtext">Please wait, this may take a moment...</div>
    </div>
    <div class="container">
        <h1>Create Index</h1>
        <form method="POST" action="{{ url_for('create_index') }}" enctype="multipart/form-data" onsubmit="document.getElementById('loadingOverlay').classList.add('active');">
            <div class="form-group">
                <label for="name">Index Name</label>
                <input type="text" id="name" name="name" required placeholder="Enter index name">
            </div>
            <div class="form-group">
                <label for="dimensions">Vector Dimensions</label>
                <input type="number" id="dimensions" name="dimensions" value="3072" min="1" required>
            </div>
            <div class="form-group">
                <label for="chunk_size">Chunk Size</label>
                <select id="chunk_size" name="chunk_size" required>
                    <option value="">Select chunk size</option>
                    <option value="256">256</option>
                    <option value="512">512</option>
                    <option value="1024">1024</option>
                    <option value="2048">2048</option>
                    <option value="4096">4096</option>
                </select>
            </div>
            <div class="form-group">
                <label for="description">Description</label>
                <textarea id="description" name="description" rows="5" placeholder="Enter index description"></textarea>
            </div>
            <div class="form-group">
                <label for="files">Upload Files</label>
                <input type="file" id="files" name="files" multiple accept=".pdf,.txt,.docx">
            </div>
            <div class="form-group">
                <label for="url">Upload URL</label>
                <input type="text" id="url" name="url" placeholder="Paste URL Here (optional)">
            </div>
            <div class="button-group">
                <button type="button" class="back-btn" onclick="window.location.href='{{ url_for('load_page') }}'">Back</button>
                <button type="submit" class="submit-btn">Create Index</button>
            </div>
        </form>
    </div>
</body>
</html>
```

### `templates/edit_index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit Index - {{ index.name }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 40px 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        header { text-align: center; margin-bottom: 40px; }
        h1 { color: #fff; font-size: 2.5rem; font-weight: 600; }
        .subtitle { color: rgba(255,255,255,0.8); margin-top: 10px; font-size: 1.1rem; }
        .card { background: #fff; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.15); overflow: hidden; }
        .card-header { background: #f8f9fa; padding: 20px 30px; border-bottom: 1px solid #e9ecef; display: flex; justify-content: space-between; align-items: center; }
        .card-header h2 { color: #333; font-size: 1.3rem; font-weight: 600; }
        .card-body { padding: 30px; }
        .form-group { margin-bottom: 20px; }
        .form-label { display: block; margin-bottom: 8px; font-weight: 600; color: #495057; }
        .form-control { width: 100%; padding: 10px 12px; border: 1px solid #ced4da; border-radius: 6px; font-size: 1rem; }
        .form-control:focus { border-color: #667eea; outline: none; box-shadow: 0 0 0 3px rgba(102,126,234,0.1); }
        .form-control[readonly] { background-color: #e9ecef; cursor: not-allowed; }
        textarea.form-control { resize: vertical; min-height: 100px; }
        .grid-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .btn { display: inline-flex; align-items: center; justify-content: center; padding: 12px 24px; border: none; border-radius: 8px; font-size: 1rem; font-weight: 500; cursor: pointer; transition: all 0.2s ease; text-decoration: none; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; width: 100%; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(102,126,234,0.4); }
        .btn-secondary { background: #6c757d; color: #fff; font-size: 0.9rem; padding: 8px 16px; }
        .file-upload-wrapper { border: 2px dashed #ced4da; border-radius: 8px; padding: 30px; text-align: center; margin-bottom: 25px; background: #f8f9fa; }
        .file-upload-wrapper:hover { border-color: #667eea; background: #fff; }
        .status-badge { display: inline-block; padding: 6px 12px; border-radius: 20px; font-size: 0.9rem; font-weight: 500; }
        .status-active { background: #d4edda; color: #155724; }
        .status-inactive { background: #f8d7da; color: #721c24; }
        .status-pending { background: #fff3cd; color: #856404; }
        footer { text-align: center; margin-top: 40px; color: rgba(255,255,255,0.7); font-size: 0.9rem; }
        .loading-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(255,255,255,0.9); display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 9999; visibility: hidden; opacity: 0; transition: visibility 0s, opacity 0.3s linear; }
        .loading-overlay.active { visibility: visible; opacity: 1; }
        .spinner { border: 5px solid #f3f3f3; border-top: 5px solid #667eea; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; margin-bottom: 15px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .loading-text { color: #333; font-size: 18px; font-weight: 500; }
        .loading-subtext { color: #666; font-size: 14px; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="loading-overlay" id="loadingOverlay">
        <div class="spinner"></div>
        <div class="loading-text">Updating Index & Uploading Files</div>
        <div class="loading-subtext">Please wait, this may take a moment...</div>
    </div>
    <div class="container">
        <header>
            <h1>Index Manager</h1>
            <p class="subtitle">Edit Index & Upload Files</p>
        </header>
        <div class="card">
            <div class="card-header">
                <h2>Edit Index: {{ index.name }}</h2>
                <a href="/" class="btn btn-secondary">Back to List</a>
            </div>
            <div class="card-body">
                <form action="/edit_index" method="POST" enctype="multipart/form-data" onsubmit="document.getElementById('loadingOverlay').classList.add('active');">
                    <input type="hidden" name="name" value="{{ index.name }}">
                    <div class="grid-row">
                        <div class="form-group">
                            <label class="form-label">Created At</label>
                            <input type="text" class="form-control" value="{{ index.created_at }}" readonly>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Status</label>
                            <div class="form-control" style="border:none;padding:0;background:transparent;">
                                {% if index.status == 'active' %}<span class="status-badge status-active">Active</span>
                                {% elif index.status == 'inactive' %}<span class="status-badge status-inactive">Inactive</span>
                                {% else %}<span class="status-badge status-pending">Pending</span>{% endif %}
                            </div>
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Number of Documents</label>
                        <input type="text" class="form-control" value="{{ index.documents }}" readonly>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="description">Description</label>
                        <textarea id="description" name="description" class="form-control" placeholder="Enter index description...">{{ index.description }}</textarea>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Add Files to Index</label>
                        <div class="file-upload-wrapper">
                            <input type="file" name="files" class="file-input" multiple>
                            <p style="margin-top:10px;color:#6c757d;font-size:0.9rem;">Click to browse or drag PDF files here</p>
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="url">Add a Website URL to Scrape</label>
                        <input type="url" id="url" name="url" class="form-control" placeholder="https://example.com">
                        <p style="margin-top:5px;color:#6c757d;font-size:0.85rem;">Optional: Enter a URL to scrape and add its contents to this index.</p>
                    </div>
                    <button type="submit" class="btn btn-primary">Update Index & Add Files</button>
                </form>
            </div>
        </div>
        <footer><p>&copy; 2026 Brigham Young University. All rights reserved.</p></footer>
    </div>
</body>
</html>
```

### `templates/select_links.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Select Links to Scrape</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 40px 20px; }
        .container { background: white; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); padding: 40px; max-width: 700px; width: 100%; }
        h1 { color: #333; margin-bottom: 10px; font-size: 28px; text-align: center; }
        .subtitle { color: #666; text-align: center; margin-bottom: 25px; font-size: 15px; }
        .links-scroll-box { max-height: 400px; overflow-y: auto; border: 2px solid #e0e0e0; border-radius: 8px; padding: 10px; margin-bottom: 25px; background-color: #fafafa; }
        .link-item { display: flex; align-items: flex-start; padding: 12px; border-bottom: 1px solid #eee; transition: background-color 0.2s; }
        .link-item:last-child { border-bottom: none; }
        .link-item:hover { background-color: #f0f4ff; border-radius: 6px; }
        .link-item input[type="checkbox"] { margin-top: 4px; margin-right: 15px; transform: scale(1.3); cursor: pointer; }
        .link-item label { cursor: pointer; flex: 1; word-break: break-word; }
        .link-title { font-weight: 600; color: #333; display: block; margin-bottom: 4px; }
        .link-url { font-size: 13px; color: #888; display: block; }
        .button-group { display: flex; gap: 15px; }
        button, .btn-link { flex: 1; padding: 14px; border: none; border-radius: 6px; font-size: 16px; font-weight: 600; cursor: pointer; text-align: center; text-decoration: none; transition: transform 0.2s, box-shadow 0.2s; }
        .submit-btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .submit-btn:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(102,126,234,0.4); }
        .back-btn { background: #f0f0f0; color: #333; }
        .back-btn:hover { background: #e0e0e0; transform: translateY(-2px); }
    </style>
</head>
<body>
    <div class="container">
        <h1>Select Links to Scrape</h1>
        <p class="subtitle">We found the following links on <strong>{{ current_url }}</strong>. Select the ones you want to add to your RAG index.</p>
        <form action="/process_selected_links" method="POST">
            <input type="hidden" name="index_name" value="{{ index_name }}">
            <div class="links-scroll-box">
                {% for link in links %}
                    <div class="link-item">
                        <input type="checkbox" id="link_{{ loop.index }}" name="selected_links" value="{{ link['url'] }}">
                        <label for="link_{{ loop.index }}">
                            <span class="link-title">{{ link['text'] }}</span>
                            <span class="link-url">{{ link['url'] }}</span>
                        </label>
                    </div>
                {% else %}
                    <div style="text-align:center;padding:40px 20px;color:#666;"><p>No sub-links were found on this page.</p></div>
                {% endfor %}
            </div>
            <div class="button-group">
                <a href="/" class="btn-link back-btn">Cancel</a>
                <button type="submit" class="submit-btn">Add Selected to Index</button>
            </div>
        </form>
    </div>
</body>
</html>
```

### `templates/download_progress.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Processing Links...</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; }
        .container { background: white; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); padding: 40px; max-width: 500px; width: 100%; text-align: center; }
        h1 { color: #333; margin-bottom: 20px; font-size: 28px; }
        #status-text { color: #667eea; margin-bottom: 10px; font-weight: 600; }
        .stats { color: #555; font-size: 16px; margin-bottom: 25px; }
        .progress-container { width: 100%; background-color: #f0f0f0; border-radius: 8px; margin: 20px 0; overflow: hidden; box-shadow: inset 0 1px 3px rgba(0,0,0,0.1); }
        .progress-bar { height: 24px; width: 0%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); transition: width 0.4s ease, background 0.4s ease; }
        .home-button { display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 30px; border: none; border-radius: 5px; font-size: 16px; font-weight: 600; cursor: pointer; text-decoration: none; transition: transform 0.2s, box-shadow 0.2s; margin-top: 20px; }
        .home-button:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(102,126,234,0.4); }
        #button-container { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Adding URLs to Index</h1>
        <h3 id="status-text">Starting up...</h3>
        <p class="stats">Processed: <span id="completed-count">0</span> / <span id="total-count">?</span></p>
        <div class="progress-container">
            <div class="progress-bar" id="my-progress-bar"></div>
        </div>
        <div id="button-container">
            <a href="/" class="home-button">Return to Home</a>
        </div>
    </div>
    <script>
        const taskId = "{{ task_id }}";
        const pollingInterval = setInterval(checkProgress, 2000);
        function checkProgress() {
            fetch(`/status/${taskId}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById("completed-count").innerText = data.completed;
                    document.getElementById("total-count").innerText = data.total;
                    if (data.total > 0) {
                        const percentage = (data.completed / data.total) * 100;
                        document.getElementById("my-progress-bar").style.width = percentage + "%";
                    }
                    if (data.status === "completed") {
                        document.getElementById("status-text").innerText = "All Finished!";
                        document.getElementById("my-progress-bar").style.background = "#28a745";
                        document.getElementById("button-container").style.display = "block";
                        clearInterval(pollingInterval);
                    } else if (data.status === "running") {
                        document.getElementById("status-text").innerText = "Scraping and Uploading to Azure...";
                    }
                })
                .catch(error => console.error("Error fetching status:", error));
        }
    </script>
</body>
</html>
```

### `templates/success_message.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Success</title>
    <style>
        body { display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .success-container { background: white; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); padding: 40px; text-align: center; max-width: 500px; width: 90%; }
        .success-icon { font-size: 60px; color: #28a745; margin-bottom: 20px; }
        h1 { color: #333; margin: 20px 0; font-size: 28px; }
        .success-message { color: #666; font-size: 16px; line-height: 1.6; margin-bottom: 30px; }
        .home-button { display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 30px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; text-decoration: none; transition: transform 0.2s, box-shadow 0.2s; }
        .home-button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102,126,234,0.4); }
    </style>
</head>
<body>
    <div class="success-container">
        <div class="success-icon">✓</div>
        <h1>Success!</h1>
        <p class="success-message">{{ message }}</p>
        <a href="{{ url_for('load_page') }}" class="home-button">Return to Home</a>
    </div>
</body>
</html>
```

### `templates/failure_message.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Failure</title>
    <style>
        body { display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .failure-container { background: white; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); padding: 40px; text-align: center; max-width: 500px; width: 90%; }
        .failure-icon { font-size: 60px; color: #dc3545; margin-bottom: 20px; }
        h1 { color: #333; margin: 20px 0; font-size: 28px; }
        .failure-message { color: #666; font-size: 16px; line-height: 1.6; margin-bottom: 30px; }
        .home-button { display: inline-block; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 12px 30px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; text-decoration: none; transition: transform 0.2s, box-shadow 0.2s; }
        .home-button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(245,87,108,0.4); }
    </style>
</head>
<body>
    <div class="failure-container">
        <div class="failure-icon">✕</div>
        <h1>Failure</h1>
        <p class="failure-message">{{ message }}</p>
        <a href="{{ url_for('load_page') }}" class="home-button">Return to Home</a>
    </div>
</body>
</html>
```