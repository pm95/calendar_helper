import CONFIG
from flask import Flask, send_file, request

app = Flask(__name__)


@app.route('/')
def send_qr_code():
    return send_file(CONFIG.QR_CODE_FILE, mimetype='image/png')


app.run()
