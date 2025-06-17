from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import polyline

app = Flask(__name__)
CORS(app)

API_KEY = "API___KEY"  # <-- Replace this with your actual key

@app.route("/geocode-route", methods=["POST"])
def geocode_route():
    try:
        data = request.get_json()
        start_place = data.get("start_place")
        end_place = data.get("end_place")

        if not start_place or not end_place:
            return jsonify({"error": "Missing input locations"}), 400

        def get_coordinates(place):
            geo_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={place}&key={API_KEY}"
            res = requests.get(geo_url).json()
            if res["status"] != "OK":
                raise Exception(f"Geocoding failed: {res.get('error_message', 'Unknown error')}")
            loc = res["results"][0]["geometry"]["location"]
            return loc["lat"], loc["lng"]

        start_lat, start_lng = get_coordinates(start_place)
        end_lat, end_lng = get_coordinates(end_place)

        return jsonify({
            "start": {"lat": start_lat, "lng": start_lng},
            "end": {"lat": end_lat, "lng": end_lng}
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/shortest-path", methods=["POST"])
def shortest_path():
    try:
        data = request.get_json()
        start = data["start"]
        end = data["end"]

        url = (
            f"https://maps.googleapis.com/maps/api/directions/json?"
            f"origin={start['lat']},{start['lng']}&"
            f"destination={end['lat']},{end['lng']}&"
            f"key={API_KEY}"
        )

        response = requests.get(url)
        result = response.json()

        if result["status"] != "OK":
            return jsonify({
                "error": "Google API Error",
                "google_status": result["status"],
                "message": result.get("error_message", "No route found.")
            }), 400

        route = result["routes"][0]
        points = route["overview_polyline"]["points"]
        coords = polyline.decode(points)

        distance = route["legs"][0]["distance"]["text"]
        duration = route["legs"][0]["duration"]["text"]

        return jsonify({
            "path": coords,
            "distance": distance,
            "duration": duration
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
