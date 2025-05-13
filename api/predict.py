from flask import Flask, request, jsonify
import os, joblib, numpy as np
from datetime import datetime
from zoneinfo import ZoneInfo
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

# Init Firebase sekali saja
if not firebase_admin._apps:
    key_json = os.environ["SERVICE_ACCOUNT_KEY_JSON"]
    with open("/tmp/key.json", "w") as f:
        f.write(key_json)
    cred = credentials.Certificate("/tmp/key.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": os.environ["DATABASE_URL"]
    })

# Load ML model sekali saja
model = joblib.load("model/gb_model2.pkl")

def latest_value(node_dict):
    if not isinstance(node_dict, dict) or not node_dict:
        return 0
    return node_dict[sorted(node_dict.keys())[-1]]

@app.route("/", methods=["GET", "POST"])
def handler():
    # POST → manual predict; GET → cron‐triggered predict dari Firebase
    if request.method == "POST":
        data = request.get_json() or {}
        features = [
            data.get("bojongsoang", 0),
            data.get("dayeuhkolot",   0),
            data.get("Debit_Cipalasari", 0),
            data.get("Debit_Citarum",     0),
            data.get("Debit_Hilir",       0),
            data.get("TMA_hilir",         0),
            data.get("TMA_kolam",         0),
            data.get("TMA_sungai",        0),
        ]
    else:
        root = db.reference("/Polder")
        features = [
            latest_value(root.child("bojongsoang").get()),
            latest_value(root.child("dayeuhkolot").get()),
            latest_value(root.child("Debit_Cipalasari").get()),
            latest_value(root.child("Debit_Citarum").get()),
            latest_value(root.child("Debit_Hilir").get()),
            latest_value(root.child("TMA_Hilir").get()),
            latest_value(root.child("TMA_Kolam").get()),
            latest_value(root.child("TMA_Sungai").get()),
        ]

    arr = np.array(features, dtype=float).reshape(1, -1)
    pump_pred, alert_pred = model.predict(arr)[0]

    ts = datetime.now(ZoneInfo("Asia/Jakarta")).strftime("%Y-%m-%d-%H_%M_%S")
    ref = db.reference("/Polder")
    ref.child("pump_on").child(ts).set(int(pump_pred))
    ref.child("status_banjir").child(ts).set(int(alert_pred))

    return jsonify({"pump_on": pump_pred, "alert_level": alert_pred})
