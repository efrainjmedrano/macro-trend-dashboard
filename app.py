from flask import Flask, jsonify, render_template
import requests
import pandas as pd
import plotly.graph_objects as go
import threading
import time

app = Flask(__name__)

data_cache = {
    "inflation": [2.5, 2.7, 2.6],
    "cot": [5000, 5200, 5100],
    "forex": {"EUR/USD": 1.12, "GBP/USD": 1.30},
    "score": 0
}

def calculate_score():
    inflation = data_cache["inflation"][-1] if data_cache["inflation"] else 0
    cot = data_cache["cot"][-1] if data_cache["cot"] else 0
    forex_strength = sum(data_cache["forex"].values()) / len(data_cache["forex"]) if data_cache["forex"] else 0
    
    score = (cot / 1000) + (forex_strength * 10) - (inflation * 2)
    data_cache["score"] = round(score, 2)

def fetch_macro_data():
    while True:
        try:
            inflation_rate = requests.get("https://api.example.com/inflation").json()
            cot_report = requests.get("https://api.example.com/cot").json()
            currency_pairs = requests.get("https://api.example.com/forex").json()
            
            data_cache["inflation"] = inflation_rate
            data_cache["cot"] = cot_report
            data_cache["forex"] = currency_pairs
            
            calculate_score()
            print("Updated macroeconomic data and score.")
        except Exception as e:
            print("Error fetching data:", e)
        time.sleep(300)

threading.Thread(target=fetch_macro_data, daemon=True).start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def get_data():
    return jsonify(data_cache)

@app.route("/chart")
def chart():
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=data_cache["inflation"], mode='lines+markers', name='Inflation Rate'))
    fig.update_layout(title='Inflation Trend', xaxis_title='Time', yaxis_title='Inflation %')
    
    return fig.to_json()

@app.route("/score")
def get_score():
    return jsonify({"score": data_cache["score"]})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
