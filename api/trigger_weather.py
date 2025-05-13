from flask import Flask, jsonify
import os
import firebase_admin
from firebase_admin import credentials, db
from model.bmkg_api import fetch_all_locations

app = Flask(__name__)

# Init Firebase sekali saja
if not firebase_admin._apps:
    key_json = os.environ["floody-252ef-firebase-adminsdk-fbsvc-19378a91dd"]
    with open("/tmp/key.json", "w") as f:
        f.write(key_json)
    cred = credentials.Certificate("/tmp/key.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": os.environ["https://console.firebase.google.com/project/floody-252ef/database/floody-252ef-default-rtdb/data/~2F"]
    })

@app.route("/", methods=["GET", "POST"])
def handler():
    all_data = fetch_all_locations()
    ref = db.reference("/Polder")
    for lokasi, data in all_data.items():
        loc_ref = ref.child(lokasi)
        if "error" in data:
            loc_ref.set(data)
        else:
            for waktu, tp in data.items():
                loc_ref.child(waktu).set(tp)
    return jsonify({"status": "success", "message": "Weather data uploaded"})
