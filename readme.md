# PDF Highlighter

A **Flask-based web application** that allows users to upload a PDF, search for specific text, and highlight it with customizable colors. The modified PDF can then be downloaded with the highlighted text.

See example image for the overview.

---

## Features
- **Upload PDFs**: Upload any PDF document from your computer.
- **Text Highlighting**: Search and highlight specific text in the PDF.
- **Download PDF**: Download the highlighted PDF for local use.
- **Custom Colors**: Highlight text with a customizable color.
 ### Note: The text highlight is default yellow as provided by PyMuPdf

---

## Demo
1. Open the app in your browser.
2. Upload a PDF file.
3. Enter the text you want to highlight.
4. Download the highlighted PDF.

---

## Installation

### Prerequisites
- Python 3.7 or higher
- `pip` (Python package manager)

### Steps
1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/pdf-highlighter.git
   cd pdf-highlighter
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the Flask server:
   ```bash
   python app.py
   ```

5. Open your browser and go to:
   ```
   http://127.0.0.1:5000/
   ```

---

## Dependencies
- [Flask](https://flask.palletsprojects.com/) - Web framework for Python
- [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/) - Library for PDF text manipulation

Install all dependencies using:
```bash
pip install -r requirements.txt
```

---

## Future Improvements
- Allow multi-color highlighting for different search terms.
- Include a preview of the highlighted text in the UI.

---
