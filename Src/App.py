from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder="../frontend", static_url_path="/")
CORS(app)

@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route("/api")
def home():
    return jsonify({
        "message": "API de Productos con Autenticación JWT",
        "endpoints": {
            "login": "/api/auth/login",
            "register": "/api/auth/register",
            "productos": "/api/products"
        }
    })

if __name__ == "__main__":
    app.run(debug=True)
