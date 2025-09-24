import os, uuid
from flask import Flask, render_template, request
from PIL import Image
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
SUPPORTED = {'.jpg','.jpeg','.png','.gif','.bmp','.tif','.tiff','.pcx'}

def get_info(file_storage):
    try:
        img = Image.open(file_storage)
        w,h = img.size
        dpi = img.info.get('dpi',(None,None))[0] or 'N/A'
        depth = {'1':1,'L':8,'P':8,'RGB':24,'RGBA':32,'CMYK':32}.get(img.mode,'Unknown')
        compression = img.info.get('compression','N/A')
        img.close()
        return [file_storage.filename,f"{w}x{h}",dpi,f"{depth} bit",compression]
    except Exception:
        return None

@app.route("/", methods=["GET","POST"])
def index():
    data = []
    if request.method == "POST":
        folderfiles = request.files.getlist('folderfiles')
        if folderfiles and folderfiles[0].filename != '':
            with ThreadPoolExecutor(max_workers=12) as executor:  # 12 потоков для ускорения
                results = executor.map(get_info, folderfiles)
                data = [r for r in results if r]
        return render_template("index.html", data=data)
    return render_template("index.html", data=None)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
