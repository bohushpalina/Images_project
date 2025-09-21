import os, zipfile, shutil, uuid
from flask import Flask, render_template, request, redirect, url_for
from PIL import Image

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

SUPPORTED = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tif', '.tiff', '.pcx'}

def extract_zip(file_path):
    folder_name = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()))
    os.makedirs(folder_name, exist_ok=True)
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(folder_name)
    return folder_name

def get_image_info(path):
    try:
        with Image.open(path) as img:
            width, height = img.size
            dpi = img.info.get('dpi', (None, None))[0]
            mode = img.mode
            compression = img.info.get('compression', 'N/A')
            depth = {
                '1': 1, 'L': 8, 'P': 8, 'RGB': 24,
                'RGBA': 32, 'CMYK': 32
            }.get(mode, 'Unknown')
            return [os.path.basename(path), f"{width}x{height}", dpi or 'N/A',
                    f"{depth} bit", compression]
    except Exception:
        return None

def scan_folder(folder):
    data = []
    for root, _, files in os.walk(folder):
        for name in files:
            ext = os.path.splitext(name)[1].lower()
            if ext in SUPPORTED:
                info = get_image_info(os.path.join(root, name))
                if info:
                    data.append(info)
    return data

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'zipfile' not in request.files:
            return redirect(url_for('index'))
        file = request.files['zipfile']
        if file.filename == '':
            return redirect(url_for('index'))

        zip_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(zip_path)
        folder = extract_zip(zip_path)
        os.remove(zip_path)

        data = scan_folder(folder)

        # Чистим старые папки (необязательно, но чтобы не копилось)
        shutil.rmtree(folder, ignore_errors=True)

        return render_template("index.html", data=data)
    return render_template("index.html", data=None)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
