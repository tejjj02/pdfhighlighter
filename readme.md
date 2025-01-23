# PDF Highlighter

A FastAPI-based web application that highlights words in PDF documents.

## Features
- Highlights multi-word phrases in PDFs
- Preserves original PDF formatting
- Handles punctuation as part of search terms
- Case-sensitive matching
- Generates combined highlights for phrases spanning multiple lines
- Exports highlighting metadata (positions, pages) in JSON format

## Installation

1. **Prerequisites**:
   - Python 3.7+
   - pip package manager

2. **Clone repository**:
   ```bash
   git clone https://github.com/tejjj02/pdf-highlighter.git
   cd pdf-highlighter
3. **Running the Application**:
   ```bash
   uvicorn main:app --reload
4. **Web interface guide**:
   - Upload pdf
   - Enter the phrase to highlight
   - After processing, use the "Download Highlighted PDF" button
   - Access /get-metadata for highlight position data
## 5. API Documentation

### Endpoints

| Endpoint      | Method | Description                          | Parameters           |
|---------------|--------|--------------------------------------|----------------------|
| `/`           | `GET`  | Web interface for PDF upload         | -                    |
| `/highlight`  | `POST` | Process PDF and add highlights       | PDF file, search text |
| `/download`   | `GET`  | Download highlighted PDF             | -                    |
| `/get-metadata`| `GET`  | Retrieve highlight metadata (JSON)   | -                    |

