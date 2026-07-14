import os
from flask import Flask, render_template, request, send_file
from pypdf import PdfReader, PdfWriter

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def compress_pdf(input_path, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        # Enable content stream compression
        page.compress_content_streams()
        writer.add_page(page)
    
    with open(output_path, "wb") as f:
        writer.write(f)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "沒有上傳檔案", 400
        
        file = request.files['file']
        if file.filename == '':
            return "未選擇檔案", 400

        if file and file.filename.endswith('.pdf'):
            input_path = os.path.join(UPLOAD_FOLDER, "temp_input.pdf")
            output_path = os.path.join(UPLOAD_FOLDER, "compressed_output.pdf")
            
            file.save(input_path)
            
            try:
                compress_pdf(input_path, output_path)
                return send_file(
                    output_path, 
                    as_attachment=True, 
                    download_name=f"compressed_{file.filename}"
                )
            except Exception as e:
                return f"壓縮失敗: {str(e)}", 500
            finally:
                if os.path.exists(input_path):
                    os.remove(input_path)

    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
