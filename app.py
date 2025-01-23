from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, HTMLResponse
import fitz  # PyMuPDF
import json
import os

app = FastAPI()
# Directories 
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def highlight_pdf(file_path, search_texts):
    doc = fitz.open(file_path)
    highlights = []
    highlight_group = 1

    for text in search_texts:
        # Split the search phrase into words, preserving punctuation and whitespace handling
        search_words = text.strip().split()
        if not search_words:
            continue  # Skip empty search terms

        for page_num in range(len(doc)):
            page = doc[page_num]
            words = page.get_text("words")
            matches = []

            # Check each possible starting position for the word sequence
            for i in range(len(words) - len(search_words) + 1):
                sequence_match = True
                # Verify if the next words match the search_words sequence exactly
                for j in range(len(search_words)):
                    if words[i + j][4] != search_words[j]:
                        sequence_match = False
                        break
                
                if sequence_match:
                    # Collect bounding boxes of all words in the sequence
                    bboxes = [words[i + j][:4] for j in range(len(search_words))]
                    # Combine bboxes into a single rectangle
                    x0 = min(bbox[0] for bbox in bboxes)
                    y0 = min(bbox[1] for bbox in bboxes)
                    x1 = max(bbox[2] for bbox in bboxes)
                    y1 = max(bbox[3] for bbox in bboxes)
                    combined_rect = fitz.Rect(x0, y0, x1, y1)
                    matches.append(combined_rect)

            # Add highlights and metadata for matches found on this page
            if matches:
                highlight_label = f"Highlight {highlight_group}"
                highlight_group += 1
                # Add all matched rectangles as highlights
                for rect in matches:
                    page.add_highlight_annot(rect)
                # Record metadata
                highlights.append({
                    "group": highlight_label,
                    "text": text,
                    "page": page_num + 1,
                    "coordinates": [[rect.x0, rect.y0, rect.x1, rect.y1] for rect in matches]
                })

    output_path = os.path.join(OUTPUT_FOLDER, "highlighted_output.pdf")
    doc.save(output_path)
    doc.close()

    # Save metadata to JSON file
    with open("highlighted_metadata.json", "w") as f:
        json.dump(highlights, f, indent=4)
    
    return output_path

# Updated HTML Form to clarify input format
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PDF Highlighter</title>
    </head>
    <body>
        <h1>Upload PDF to Highlight</h1>
        <form action="/highlight" method="post" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <input type="text" name="search_texts" placeholder="Enter phrase to highlight (include punctuation)" required>
            <input type="submit" value="Upload and Highlight">
        </form>

        <h2>Download Highlighted PDF</h2>
        <form action="/download" method="get">
            <button type="submit">Download Highlighted PDF</button>
        </form>
    </body>
    </html>
    """

# Modified to treat entire input as a single search phrase
@app.post("/highlight")
async def highlight(file: UploadFile = File(...), search_texts: str = Form(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Process the entire input as a single search phrase
    search_terms = [search_texts.strip()]  # No comma splitting
    highlighted_pdf_path = highlight_pdf(file_path, search_terms)

    return {
        "message": "PDF processed successfully",
        "download_url": "/download",
        "metadata_url": "/get-metadata"
    }

# The /download and /get-metadata endpoints remain unchanged
@app.get("/download")
async def download_pdf():
    highlighted_pdf_path = os.path.join(OUTPUT_FOLDER, "highlighted_output.pdf")
    if os.path.exists(highlighted_pdf_path):
        return FileResponse(highlighted_pdf_path, media_type='application/pdf', filename="highlighted_output.pdf")
    return {"error": "File not found"}

@app.get("/get-metadata")
async def get_metadata():
    if os.path.exists("highlighted_metadata.json"):
        with open("highlighted_metadata.json", "r") as f:
            metadata = json.load(f)
        return metadata
    return {"error": "No metadata available"}


