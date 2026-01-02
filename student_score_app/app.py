from flask import Flask, render_template, request
import pickle
import numpy as np
import pandas as pd
import os

app = Flask(__name__)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        hours = float(request.form.get("hours", 0))
        sleep = float(request.form.get("sleep", 0))
        attendance = float(request.form.get("attendance", 0))
        assignments = float(request.form.get("assignments", 0))
        X = np.array([[hours, sleep, attendance, assignments]])
        pred = model.predict(X)[0]
        pred = round(float(pred), 2)
        return render_template("result.html", prediction=pred, inputs={"Hours":hours,"Sleep":sleep,"Attendance(%)":attendance,"Assignments":assignments})
    except Exception as e:
        return f"Error: {e}", 400

@app.route("/data")
def data():
    # optional: show first rows of dataset if present
    csv_path = os.path.join(os.path.dirname(__file__), "..", "student_performance.csv")
    # if original csv not present, skip
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        return df.head(20).to_html(classes='table table-striped', index=False)
    return "Dataset preview not available."

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=7860)
