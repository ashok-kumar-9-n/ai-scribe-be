# 🧠 AI-Scribe Backend Service

This backend service provides multiple endpoints to handle audio transcription, SOAP note generation, and medical record management.

## 🔹 Backend (BE) Service - Local Run Setup

1. **Create and Activate Virtual Environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install Python Dependencies**

   ```bash
   pip3 install -r requirements.txt
   ```

3. **Run the Backend Server**

   ```bash
   python3 main.py
   ```

   This starts the backend on:

   ```
   http://localhost:8000
   ```

---

## 🐳 Alternatively: Docker Setup

```bash
docker compose up
```

> A `docker-compose.yml` file is included in the project.


## 📦 Postman Collection

A Postman collection is included for testing the APIs:
- **File:** `AI-Scribe.postman_collection.json`
- You can import this into Postman to test all available endpoints easily.

## 🌐 Live Deployment

The backend service is deployed at:

```
http://13.49.223.112:8000
```

All API endpoints mentioned below can be accessed through this base URL.

---

## 🧪 API Endpoints

### `/api/s3`

- `POST /upload`  
  Upload any media file or media URL to S3 and return the `s3_url`.

---

### `/api/deepgram`

- `POST /get-transcript`  
  Get the transcript of the `media_url` in a structured format with a proper timeline (same as stored in DB).

---

### `/api/llm`

- `POST /generate-soap-notes`  
  Generate SOAP notes based on a given transcript.

---

### `/api/record`

- `POST /generate-soap`  
  Accepts either a media file or media URL, along with `patient_id` and `doctor_id`.  
  Internally uploads the media to S3, fetches Deepgram transcript, generates SOAP notes, and saves everything to the database.

- `POST /save-encounter`  
  Save an encounter record of the doctor with the patient.

- `POST /fetch-records`  
  Fetch all medical records for a particular doctor using `doctor_id`.

- `POST /get-record-by-id`  
  Retrieve details of a specific medical record by `record_id`.

---


