import fitz 
from flask import Flask, render_template, request, send_file
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def highlight_pdf(input_path, output_path, search_text):
    try:
        pdf_document = fitz.open(input_path)
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text_instances = page.search_for(search_text)
            for inst in text_instances:
                highlight = page.add_highlight_annot(inst)
                if highlight:
                    
                    highlight.set_colors(stroke=None, fill=(0.2, 1, 0.5)) 
                    highlight.update() 
        pdf_document.save(output_path)
        pdf_document.close()
        return True
    except Exception as e:
        print(f"Error during highlighting: {e}")
        return False




@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded_file = request.files["pdf_file"]
        search_text = request.form["search_text"]

        if uploaded_file and search_text:
            input_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
            output_path = os.path.join(OUTPUT_FOLDER, f"highlighted_{uploaded_file.filename}")

            uploaded_file.save(input_path)
            success = highlight_pdf(input_path, output_path, search_text)
            if success:
                return send_file(output_path, as_attachment=True)
            else:
                return "Error highlighting the PDF.", 500

    return render_template("index.html") #location of html file

if __name__ == "__main__":
    app.run(debug=True)
