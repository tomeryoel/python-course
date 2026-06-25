# Intelligent Cloud Document Analyst — n8n + Gemini AI

## Project Overview

This project implements an intelligent cloud document analysis workflow using **n8n**, **Google Gemini API**, **Python FastAPI**, **Google Drive**, **Google Sheets**, and **Gmail**.

The system detects new documents uploaded to a Google Drive `incoming_docs` folder, extracts their text, sends the extracted content to Gemini for structured analysis, enriches the result through a custom Python Metadata API, writes the final result to Google Sheets, sends an email notification, and creates a Markdown summary file in an `output_docs` folder.

The selected scenario for this project is:

**Cybersecurity Incident Logs — alert reports, SIEM exports, phishing reports, suspicious login alerts, and vulnerability scan summaries.**

---

## Main Workflow

The workflow performs the following steps:

1. **File Detection**
   A Google Drive Trigger watches the `incoming_docs` folder for newly uploaded files.

2. **File Download**
   The detected file is downloaded using the Google Drive node.

3. **File Type Routing**
   A Switch node routes the file based on its extension:

   * `txt`
   * `pdf`
   * `docx` optional route

4. **Text Extraction**
   The workflow extracts text from the uploaded document.

5. **Gemini AI Analysis**
   The extracted text is sent to the Google Gemini API using an HTTP Request node.
   Gemini returns a structured JSON response containing:

   * summary
   * classification
   * sentiment
   * entities
   * action items
   * confidence score

6. **JSON Parsing**
   A JavaScript Code node parses and normalizes the Gemini response.

7. **Metadata Enrichment**
   The parsed Gemini result is sent to a Python FastAPI service.
   The API enriches the result with:

   * document ID
   * internal department
   * sensitivity level
   * routing tag
   * processing timestamp
   * adjusted confidence score

8. **Google Sheets Output**
   The final enriched result is appended as a new row in Google Sheets.

9. **Gmail Notification**
   A Gmail node sends an email summary after each successful document processing run.

10. **Summary File Creation**
    A Markdown summary file is created in the Google Drive `output_docs` folder.

---

## Architecture

```text
Google Drive incoming_docs/
        ↓
Google Drive Trigger
        ↓
Download File
        ↓
Switch by File Type
        ↓
Text Extraction
        ↓
Gemini Analysis
        ↓
Parse Gemini JSON
        ↓
Python FastAPI Metadata Enrichment
        ↓
Combine Results
        ↓
Google Sheets + Gmail + output_docs Summary File
```

---

## Technologies Used

* n8n
* Google Gemini API
* Google Drive
* Google Sheets
* Gmail
* Python
* FastAPI
* Uvicorn
* JavaScript Code node in n8n
* Docker / self-hosted n8n

---

## Project Structure

```text
n8n-document-analyst/
│
├── metadata_api/
│   ├── main.py
│   └── requirements.txt
│
├── samples/
│   ├── phishing_incident.txt
│   ├── vulnerability_scan.txt
│   └── suspicious_login.txt
│
├── screenshots/
│   └── relevant project screenshots
│
├── n8n_workflow_export.json
├── README.md
└── .gitignore
```

---

## Metadata API

The project includes a Python FastAPI microservice located under:

```text
metadata_api/
```

### API Endpoints

| Method | Endpoint        | Description                                         |
| ------ | --------------- | --------------------------------------------------- |
| GET    | `/health`       | Health check endpoint                               |
| GET    | `/categories`   | Returns supported cybersecurity document categories |
| POST   | `/enrich`       | Enriches Gemini JSON output with business metadata  |
| POST   | `/sensitivity`  | Classifies document sensitivity                     |
| POST   | `/extract-docx` | Optional DOCX extraction endpoint                   |

---

## Running the Metadata API

Open PowerShell inside the `metadata_api` folder:

```powershell
cd metadata_api
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run the API:

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Health check:

```text
http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "metadata-api"
}
```

---

## Google Sheets Output

Each processed document is appended to a Google Sheet with the following fields:

* document_id
* filename
* file_type
* processed_at
* classification
* department
* sentiment
* confidence_score
* adjusted_confidence_score
* summary
* routing_tag
* sensitivity
* action_items

---

## Sample Documents

The `samples` folder contains synthetic cybersecurity documents used for testing:

* `phishing_incident.txt`
* `vulnerability_scan.txt`
* `suspicious_login.txt`

These files simulate common cybersecurity investigation documents and are used as safe input examples for the workflow.

---

## Screenshots

The `screenshots` folder contains relevant screenshots showing:

* Successful n8n workflow execution
* Google Sheets output
* Gmail notification
* Google Drive summary file output
* Metadata API running
* Workflow structure

---

## Security Notes

The exported n8n workflow file does not include the real Gemini API key.

Before committing to GitHub, the Gemini API key should be replaced with:

```text
YOUR_GEMINI_API_KEY_HERE
```

The actual API key should remain only inside the local/private n8n environment and must not be committed to GitHub.

---

## Implementation Challenges

During the project, several implementation challenges were handled:

* Google OAuth configuration for Drive, Sheets, and Gmail
* Google Drive access limitations on the local machine
* Gemini API authentication and API key validation
* Correct JSON body formatting for the Gemini HTTP request
* Parsing and normalizing Gemini structured JSON output
* Connecting n8n running in Docker to the local FastAPI service using `host.docker.internal`
* Mapping enriched metadata correctly into Google Sheets

---

## Final Status

The workflow was successfully tested end-to-end with a cybersecurity incident document.

The final workflow successfully:

* detects a new document
* downloads the file
* extracts text
* sends content to Gemini
* parses structured JSON
* enriches the result through FastAPI
* writes the result to Google Sheets
* sends a Gmail notification
* creates a Markdown summary file in Google Drive
