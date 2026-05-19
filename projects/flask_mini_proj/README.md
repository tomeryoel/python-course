# Cybersecurity RAG Assistant

## Project Overview

This project is a Retrieval-Augmented Generation (RAG) web application built with Flask.

The system allows users to ask cybersecurity-related questions and receive grounded answers based on a local cybersecurity knowledge base. The application combines FAISS semantic retrieval with Google's Gemini LLM to generate context-aware responses.

The project demonstrates a complete RAG pipeline including document preprocessing, embeddings generation, vector search, LLM integration, conversation memory, and a working web interface.

---

## Topic

The selected topic for this project is cybersecurity.

The knowledge base focuses on common cyber threats and security concepts, including:

- Brute force attacks
- Ransomware
- SQL injection
- Phishing attacks

---

## Main Features

- Flask web application
- HTML/CSS/JavaScript frontend
- FAISS vector database
- Hugging Face embeddings
- Gemini LLM integration
- Context-based response generation
- SQLite conversation memory
- Retrieved context display
- Loading indicators
- Basic error handling
- Retry logic for Gemini API calls

---

## Project Architecture

```text
User Question
↓
Frontend Interface
↓
Flask Backend
↓
FAISS Semantic Retrieval
↓
Relevant Context
↓
Gemini LLM
↓
Generated Response
```

---

## Knowledge Base

The knowledge base contains local cybersecurity-related `.txt` documents stored inside the `data/` folder.

### Documents Used

- `Brute Force Attack Patterns.txt`
- `Ransomware Guide.txt`
- `SQL Injection.txt`
- `Understanding and Mitigating Phishing Attacks.txt`

The content was collected from real cybersecurity educational resources and converted into local text files.

---

## Chunking and Embeddings

The documents are split into smaller sentence-based chunks before generating embeddings.

Chunking improves semantic retrieval by allowing the system to retrieve only the most relevant parts of a document instead of entire files.

The project uses Hugging Face embeddings to convert chunks into vector representations.

---

## FAISS Vector Database

FAISS is used to store and retrieve embeddings based on semantic similarity.

The retrieval pipeline includes:

1. Loading documents
2. Splitting text into chunks
3. Generating embeddings
4. Creating a FAISS index
5. Retrieving relevant chunks for user questions

The FAISS index is cached locally to improve performance and avoid regenerating embeddings on every run.

---

## RAG Pipeline

The RAG pipeline works as follows:

1. The user submits a question.
2. FAISS retrieves the most relevant chunks.
3. Retrieved context is injected into the prompt.
4. Gemini generates a grounded response.
5. The response and retrieved context are displayed in the frontend.

The model is instructed to answer only from the retrieved context in order to reduce hallucinations.

If the context does not contain enough information, the system responds with:

```text
I do not have enough information in the provided documents.
```

---

## Retrieval Configuration

```python
TOP_K = 3
BATCH_SIZE = 16
```

- `TOP_K = 3` retrieves the three most relevant chunks.
- `BATCH_SIZE = 16` is used during embedding generation.

---

## Prompt Design

The prompt instructs Gemini to answer only using the retrieved context and avoid using external knowledge.

Example prompt structure:

```text
You are a helpful cybersecurity RAG assistant.

Answer the user's question ONLY using the provided context.

Rules:
1. Use only the information found in the context.
2. If the context does not contain enough information, respond exactly with:
   "I do not have enough information in the provided documents."
3. Do not use external knowledge.
4. Do not make up information.
5. Keep the answer simple and clear.
```

---

## Web Application

The frontend was built using HTML, CSS, and JavaScript.

The application includes:

- Chat interface
- User input field
- Model response display
- Retrieved context display
- Loading indicators
- Clear chat functionality

Run locally:

```bash
python app.py
```

Open in browser:

```text
http://127.0.0.1:5000/chat
```

---

## Conversation Memory

The application uses SQLite to store:

- User messages
- Assistant responses
- Session identifiers

This allows the assistant to maintain chat history during the active session.

---

## Validation and Testing

The system was tested using cybersecurity-related and irrelevant questions.

### Example Questions

```text
How can organizations reduce the risk of phishing attacks?
```

```text
What are the best ways to prevent SQL injection attacks?
```

```text
What techniques can administrators use to protect users from brute force attacks?
```

```text
What are common signs of a ransomware infection?
```

### Irrelevant Question Test

```text
Who won the FIFA World Cup in 2022?
```

Expected behavior:

```text
I do not have enough information in the provided documents.
```

This test verifies that the model does not rely on external knowledge when the retrieved context is irrelevant.

---

## Screenshots / Demo

Screenshots of the application are included in the `screenshots/` folder.

screenshots:

```text
screenshots/homepage.png
screenshots/phishing_test.png
screenshots/sql_injection_test.png
screenshots/ransomware_test.png
screenshots/irrelevant_question_test.png
```

---

## Error Handling

The project includes basic error handling for:

- Empty user input
- Gemini API request failures
- Retry attempts during failed requests

---

## Performance Optimization

To improve performance:

- FAISS indexes are cached locally
- Embeddings are reused between runs
- Batch embedding generation is used

---

## Possible Improvements

Future improvements could include:

- PDF document support
- Better chunk overlap strategy
- Improved retrieval ranking
- Streaming responses
- Multi-user support
- Enhanced UI/UX

---

## Reflection

This project provided hands-on experience with building a complete RAG application using FAISS, embeddings, semantic retrieval, and LLM integration.

One of the main challenges was ensuring that the model answered only from the retrieved context and did not rely on external knowledge.

Overall, the project demonstrates a complete end-to-end RAG system with a cybersecurity knowledge base, semantic retrieval, conversation memory, and a Flask web interface.