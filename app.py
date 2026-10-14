
from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

# -----------------------------
# HOME PAGE
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# PWA SERVICE WORKER
# -----------------------------
@app.route("/sw.js")
def service_worker():
    response = app.send_static_file("sw.js")
    response.headers["Service-Worker-Allowed"] = "/"
    response.headers["Content-Type"] = "application/javascript"
    response.headers["Cache-Control"] = "no-cache"
    return response


# -----------------------------
# HEALTH CHECK API
# -----------------------------
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "success": True,
        "message": "Rakshika AI backend is running"
    }), 200


# -----------------------------
# VEHICLE NUMBER VALIDATION
# -----------------------------
def validate_vehicle_number(vehicle_number):
    """
    Checks the basic format of an Indian vehicle registration number.
    Does not verify the vehicle against government records.
    """
    vehicle_number = vehicle_number.upper().replace(" ", "")
    pattern = r"^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{1,4}$"
    return bool(re.fullmatch(pattern, vehicle_number))


# -----------------------------
# RIDE SAFETY API
# -----------------------------
@app.route("/api/ride-check", methods=["POST"])
def ride_check():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Please send valid JSON data."
        }), 400

    vehicle = str(data.get("vehicle", "")).strip().upper()
    driver = str(data.get("driver", "")).strip()
    provider = str(data.get("provider", "")).strip()

    if not vehicle:
        return jsonify({
            "success": False,
            "message": "Vehicle registration number is required."
        }), 400

    if not validate_vehicle_number(vehicle):
        return jsonify({
            "success": False,
            "message": "Vehicle number format looks invalid. Please check it."
        }), 400

    return jsonify({
        "success": True,
        "message": "Vehicle number format accepted.",
        "ride_details": {
            "vehicle": vehicle,
            "driver_provided": bool(driver),
            "provider_provided": bool(provider)
        },
        "checklist": [
            "Compare the vehicle number with your booking.",
            "Check that the driver matches your booking.",
            "Share trip details with someone you trust."
        ],
        "notice": (
            "This is only a format check. The vehicle, driver, "
            "and provider have not been independently verified."
        )
    }), 200


# -----------------------------
# PAGE NOT FOUND
# -----------------------------
@app.errorhandler(404)
def page_not_found(error):
    if request.path.startswith("/api/"):
        return jsonify({
            "success": False,
            "message": "API endpoint not found."
        }), 404

    return "Page not found", 404


# -----------------------------
# RUN APPLICATION
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
