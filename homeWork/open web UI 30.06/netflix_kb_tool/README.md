# Netflix Knowledge Base + Local Movie Search Tool

## Project Overview

This homework project demonstrates an Open WebUI assistant that combines two different information sources:

1. **Knowledge Base inside Open WebUI**  
   A Kaggle CSV dataset about Netflix movies and TV shows was uploaded to Open WebUI and indexed as a Knowledge Base.

2. **Local Python Tool Server**  
   A local FastAPI server named `tools_server.py` runs on `http://127.0.0.1:5005` and calls RapidAPI MoviesDatabase to retrieve external movie or TV show information.

The goal of this project is to allow the assistant to answer questions from the uploaded dataset and also use a live external API through a local Python tool.

---

## Dataset

Dataset used:

- **Netflix Movies and TV Shows**
- Source: Kaggle
- File used: `netflix_titles.csv`

The dataset contains metadata about Netflix content, such as:

- `show_id`
- `type`
- `title`
- `director`
- `cast`
- `country`
- `date_added`
- `release_year`
- `rating`
- `duration`
- `listed_in`
- `description`

---

## Technologies Used

- Open WebUI
- Kaggle CSV dataset
- Python
- FastAPI
- Uvicorn
- Requests
- python-dotenv
- RapidAPI MoviesDatabase
- Open WebUI Knowledge Base
- Open WebUI Tool

---

## Assignment Requirement Mapping

| Requirement | Implementation |
|---|---|
| Upload a CSV from Kaggle | Uploaded `netflix_titles.csv` from Kaggle |
| Let the Web UI index it as a Knowledge Base | Created `Netflix Shows KB` in Open WebUI |
| Build a local Python server | Implemented `tools_server.py` using FastAPI |
| Server runs locally | Server runs on `http://127.0.0.1:5005` |
| Use RapidAPI relevant to the dataset | Used RapidAPI MoviesDatabase |
| Declare a Web UI Function / Tool | Created an Open WebUI Tool that calls the local server |
| Assistant can use KB | Tested questions against the uploaded Netflix dataset |
| Assistant can use live API/tool | Tested the local endpoint and server logs with RapidAPI responses |

---

## Project Structure

```text
netflix_kb_tool/
│
├── tools_server.py
├── netflix_titles.csv
├── requirements.txt
├── .env.example
├── README.md
└── screenshots/
```

> Note: The `.env` file is intentionally not included in GitHub because it contains the RapidAPI key.

---

## Environment Variables

Create a local `.env` file in the project folder:

```env
RAPIDAPI_KEY=your_rapidapi_key_here
RAPIDAPI_HOST=moviesdatabase.p.rapidapi.com
```

The submitted project includes `.env.example` instead of the real `.env` file.

---

## Installation

From the project folder, create and activate a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install fastapi uvicorn[standard] requests python-dotenv
```

Optional, if SSL certificate issues occur on Windows:

```powershell
pip install --upgrade certifi python-certifi-win32
```

---

## Running the Local Server

Run the FastAPI server:

```powershell
uvicorn tools_server:app --host 127.0.0.1 --port 5005 --reload
```

The server is available at:

```text
http://127.0.0.1:5005
```

---

## API Endpoints

### Health Check

```text
GET /health
```

Example URL:

```text
http://127.0.0.1:5005/health
```

Expected result:

```json
{
  "status": "ok",
  "message": "tools_server.py is running",
  "rapidapi_host": "moviesdatabase.p.rapidapi.com",
  "rapidapi_key_configured": true
}
```

### Search Movie or TV Title

```text
GET /search_title?title=Inception
```

Example URL:

```text
http://127.0.0.1:5005/search_title?title=Inception
```

Expected result includes:

```json
{
  "searched_title": "Inception",
  "source": "RapidAPI MoviesDatabase",
  "top_results": []
}
```

---

## Open WebUI Knowledge Base

In Open WebUI:

1. Opened `Workspace`.
2. Opened `Knowledge`.
3. Created a new Knowledge Base named `Netflix Shows KB`.
4. Uploaded `netflix_titles.csv`.
5. Waited for indexing to complete.
6. Tested the Knowledge Base in chat using questions about the uploaded dataset.

---

## Open WebUI Tool

An Open WebUI Tool named `Netflix Movie Search Tool` was created.

The tool calls the local FastAPI endpoint:

```text
http://127.0.0.1:5005/search_title
```

The tool receives a movie or TV show title and returns live external information from RapidAPI MoviesDatabase.

---

## Testing Evidence

The following screenshots were prepared as evidence:

```text
01_kaggle_dataset_page.png
02_project_csv_file.png
03_openwebui_knowledge_base.png
04_knowledge_base_chat_test.png
05_rapidapi_endpoint_test.png
06_local_python_server_running.png
07_local_server_health_check.png
08_local_server_search_title_test.png
09_fastapi_docs_endpoints.png
10_openwebui_tool_configuration.png
```

These screenshots demonstrate:

- Kaggle dataset selection
- CSV file inside the project
- Open WebUI Knowledge Base creation
- Knowledge Base chat test
- RapidAPI endpoint test
- Local FastAPI server running
- Health check endpoint
- Search endpoint returning movie data
- FastAPI documentation page
- Open WebUI Tool configuration

---

## Challenges and Fixes

During development, I encountered two main issues:

1. **SSL certificate verification error**  
   Python initially failed to connect to RapidAPI because of a certificate verification issue.  
   This was resolved by updating certificate-related packages on Windows.

2. **RapidAPI 403 Forbidden error**  
   The RapidAPI key was accidentally copied with an extra apostrophe from the RapidAPI code snippet.  
   Removing the extra character fixed the issue, and the local server successfully returned `200 OK`.

In my local Open WebUI instance, the chat tool selector did not always persist the selected tool. Therefore, I verified the tool chain using the Open WebUI Tool configuration, the local FastAPI endpoint response, and the server logs.

---

## Summary

This project demonstrates how to combine a static Knowledge Base with a live API tool:

- The Knowledge Base answers questions from the uploaded Netflix CSV dataset.
- The local Python server calls RapidAPI MoviesDatabase.
- The Open WebUI Tool connects the assistant to the local server.
- The project shows a complete flow from dataset indexing to external API integration.
