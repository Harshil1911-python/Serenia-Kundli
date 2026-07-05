"""
Jyotish Kundli System - Main Flask Application
Run: python ap.py
Then open: http://localhost:5000
"""
from flask import Flask, request, jsonify, send_file, render_template_string
import json, io, os, sys, traceback

sys.path.insert(0, os.path.dirname(__file__))
from astro_calc import calculate_kundli, calculate_gun_milan
from pdf_gen import generate_kundli_pdf, generate_matching_pdf

app = Flask(__name__, template_folder=os.path.dirname(__file__))

@app.route("/")
def index():
    with open(os.path.join(os.path.dirname(__file__), "index.html"), encoding="utf-8") as f:
        return f.read()

@app.route("/match")
def match():
    with open(os.path.join(os.path.dirname(__file__), "match.html"), encoding="utf-8") as f:
        return f.read()

@app.route("/api/kundli", methods=["POST"])
def api_kundli():
    try:
        data = request.get_json()
        name = data.get("name", "").strip()
        gender = data.get("gender", "Male")
        dob = data.get("dob", "").strip()        # DD/MM/YYYY
        tob = data.get("tob", "").strip()        # HH:MM
        lat = float(data.get("lat", 23.0))
        lon = float(data.get("lon", 72.6))
        tz  = float(data.get("tz", 5.5))

        if not name or not dob or not tob:
            return jsonify({"error": "Missing required fields"}), 400

        result = calculate_kundli(name, gender, dob, tob, lat, lon, tz)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/kundli/pdf", methods=["POST"])
def api_kundli_pdf():
    try:
        data = request.get_json()
        kundli = calculate_kundli(
            data["name"], data["gender"], data["dob"], data["tob"],
            float(data["lat"]), float(data["lon"]), float(data["tz"])
        )
        pdf_bytes = generate_kundli_pdf(kundli)
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"Kundli_{data['name'].replace(' ','_')}.pdf"
        )
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/match", methods=["POST"])
def api_match():
    try:
        data = request.get_json()
        p1 = data["person1"]
        p2 = data["person2"]
        k1 = calculate_kundli(p1["name"], p1["gender"], p1["dob"], p1["tob"],
                               float(p1["lat"]), float(p1["lon"]), float(p1["tz"]))
        k2 = calculate_kundli(p2["name"], p2["gender"], p2["dob"], p2["tob"],
                               float(p2["lat"]), float(p2["lon"]), float(p2["tz"]))
        gun = calculate_gun_milan(k1, k2)
        return jsonify({
            "success": True,
            "kundli1": k1,
            "kundli2": k2,
            "gun_milan": gun
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/match/pdf", methods=["POST"])
def api_match_pdf():
    try:
        data = request.get_json()
        p1 = data["person1"]
        p2 = data["person2"]
        k1 = calculate_kundli(p1["name"], p1["gender"], p1["dob"], p1["tob"],
                               float(p1["lat"]), float(p1["lon"]), float(p1["tz"]))
        k2 = calculate_kundli(p2["name"], p2["gender"], p2["dob"], p2["tob"],
                               float(p2["lat"]), float(p2["lon"]), float(p2["tz"]))
        gun = calculate_gun_milan(k1, k2)
        pdf_bytes = generate_matching_pdf(k1, k2, gun)
        fname = f"Match_{p1['name'].replace(' ','_')}_and_{p2['name'].replace(' ','_')}.pdf"
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=fname
        )
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("=" * 60)
    print("  Jyotish Kundli System")
    print("  Open: http://localhost:5000")
    print("  Marriage Matching: http://localhost:5000/match")
    print("=" * 60)
    app.run(debug=True, port=5000)
