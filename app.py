from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, RedirectResponse
import fitz  # PyMuPDF
import json
import os

app = FastAPI(title="PDF Highlighter API", description="API for highlighting text in PDFs", version="1.0")

# Configuration
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Color mapping dictionary
COLOR_MAP = {
    "red": (1, 0, 0),
    "green": (0, 1, 0),
    "blue": (0, 0, 1),
    "yellow": (1, 1, 0),
    "magenta": (1, 0, 1),
    "cyan": (0, 1, 1),
    "purple": (0.5, 0, 0.5),
    "orange": (1, 0.5, 0),
    "pink": (1, 0.7, 0.9),
    "teal": (0, 0.5, 0.5)
}

def highlight_pdf(file_path, search_texts, colors=None):
    doc = fitz.open(file_path)
    highlights = []
    
    # Default color palette
    default_colors = list(COLOR_MAP.values())
    
    # Prepare colors list
    highlight_colors = colors or default_colors
    
    for idx, text in enumerate(search_texts):
        search_phrase = text.strip()  # Do NOT replace commas; treat entire text as a phrase
        if not search_phrase:
            continue

        # Get color for this highlight group
        color = highlight_colors[idx % len(highlight_colors)]
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            words = page.get_text("words")  # Extract words with bounding boxes
            matches = []

            phrase_len = len(search_phrase.split())  # Number of words in search phrase

            for i in range(len(words) - phrase_len + 1):
                match = True
                for j in range(phrase_len):
                    if words[i + j][4].strip() != search_phrase.split()[j].strip():
                        match = False
                        break

                if match:
                    # Highlight each word separately if they are on different lines
                    bboxes = [words[i + j][:4] for j in range(phrase_len)]
                    line_positions = [b[1] for b in bboxes]
                    unique_lines = list(set(line_positions))

                    if len(unique_lines) > 1:
                        for bbox in bboxes:
                            rect = fitz.Rect(*bbox)
                            annot = page.add_highlight_annot(rect)
                            annot.set_colors(stroke=color)
                            annot.update()
                            matches.append(rect)
                    else:
                        # Merge bounding boxes for a single-line phrase
                        x0 = min(b[0] for b in bboxes)
                        y0 = min(b[1] for b in bboxes)
                        x1 = max(b[2] for b in bboxes)
                        y1 = max(b[3] for b in bboxes)
                        combined_rect = fitz.Rect(x0, y0, x1, y1)

                        annot = page.add_highlight_annot(combined_rect)
                        annot.set_colors(stroke=color)
                        annot.update()
                        matches.append(combined_rect)

            if matches:
                highlights.append({
                    "group": f"Highlight {idx+1}",
                    "text": text,
                    "page": page_num + 1,
                    "color": color,
                    "coordinates": [[rect.x0, rect.y0, rect.x1, rect.y1] for rect in matches]
                })

    output_path = os.path.join(OUTPUT_FOLDER, "highlighted_output.pdf")
    doc.save(output_path)
    doc.close()

    # Save metadata
    with open("highlighted_metadata.json", "w") as f:
        json.dump(highlights, f, indent=4)
    
    return output_path



@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.post("/highlight", summary="Highlight text in a PDF")
async def process_pdf(
    file: UploadFile = File(...),
    search_texts: str = Form(...),
    colors: str = Form(None)
):
    """
    Upload a PDF file and highlight the specified phrases in the document.

    - **file**: The PDF file to process.
    - **search_texts**: Comma-separated phrases to highlight.
    - **colors**: (Optional) Comma-separated colors (e.g., "red,blue").
    """
    # Save uploaded file
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Process search terms
    # search_terms = [t.strip() for t in search_texts.split(",") if t.strip()]
    search_terms = [t.strip() for t in search_texts.split("|") if t.strip()]

    
    # Process colors
    parsed_colors = []
    if colors:
        color_inputs = [c.strip().lower() for c in colors.split(",")]
        parsed_colors = [COLOR_MAP.get(c, (1, 1, 0)) for c in color_inputs]
    
    # Process PDF
    highlighted_pdf_path = highlight_pdf(file_path, search_terms, parsed_colors)
    
    return {
        "message": "PDF processed successfully",
        "download_url": "/download",
        "metadata_url": "/get-metadata"
    }




@app.get("/download", summary="Download the highlighted PDF")
async def download_pdf():
    """
    Download the processed PDF file with highlights.
    """
    highlighted_pdf_path = os.path.join(OUTPUT_FOLDER, "highlighted_output.pdf")
    if os.path.exists(highlighted_pdf_path):
        return FileResponse(
            highlighted_pdf_path,
            media_type='application/pdf',
            filename="highlighted_document.pdf"
        )
    return {"error": "File not found. Process a PDF first."}

@app.get("/get-metadata", summary="Get metadata of highlighted text")
async def get_metadata():
    """
    Retrieve metadata about the highlighted text in the processed PDF.
    """
    if os.path.exists("highlighted_metadata.json"):
        with open("highlighted_metadata.json", "r") as f:
            metadata = json.load(f)
        return metadata
    return {"error": "No metadata available. Process a PDF first."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



