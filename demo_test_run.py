import os
import requests
import json
from pyproj import Transformer
from datetime import datetime

# --- Configuration ---
# Include Captum Integrated Gradients explanations from the evaluated model
os.environ["TOXICITY_INCLUDE_NEURAL_EXPLANATION"] = "1"

# API endpoint
API_URL = "http://127.0.0.1:8000/route"

# --- Test Case ---
# Source and Destination Coordinates (WGS84: lat, lon)
SOURCE_COORDS_WGS84 = (12.9716, 77.5946)  # Bangalore
DESTINATION_COORDS_WGS84 = (12.9795, 77.5908) # Near Cubbon Park

# Commute modes to test
COMMUTE_MODES = ["jogger", "cyclist", "two_wheeler", "car"]

# --- Coordinate Transformation ---
# Transformer to convert WGS84 to UTM Zone 43N (EPSG:32643), which is the project standard
_WGS84_TO_UTM43 = Transformer.from_crs("EPSG:4326", "EPSG:32643", always_xy=True)

def to_utm(lat, lon):
    """Converts latitude and longitude to UTM coordinates."""
    x, y = _WGS84_TO_UTM43.transform(lon, lat)
    return x, y


def get_user_input():
    """Gets user input for source, destination, and departure time."""
    try:
        source_lat = float(input("Enter source latitude (e.g., 12.9716): "))
        source_lon = float(input("Enter source longitude (e.g., 77.5946): "))
        dest_lat = float(input("Enter destination latitude (e.g., 12.9795): "))
        dest_lon = float(input("Enter destination longitude (e.g., 77.5908): "))
        
        time_str = input("Enter departure time (YYYY-MM-DD HH:MM:SS) or leave blank for now: ")
        departure_time = None
        if time_str:
            try:
                # Attempt to parse the most common format first
                datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                departure_time = time_str
            except ValueError:
                # Handle cases with extra components like milliseconds
                parts = time_str.split(":")
                if len(parts) > 2:
                    time_str = f"{parts[0]}:{parts[1]}:{parts[2].split('.')[0]}"
                    try:
                        datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                        departure_time = time_str
                        print(f"Warning: Truncated time input to '{time_str}'")
                    except ValueError:
                        print("Invalid time format. Ignoring departure time.")
                else:
                    print("Invalid time format. Ignoring departure time.")
        

        return (source_lat, source_lon), (dest_lat, dest_lon), departure_time
    except ValueError:
        print("Invalid input. Please enter valid numbers for coordinates.")
        return None, None, None


def get_commuter_counts():
    """Optionally configure a cohort to exercise capacity-aware matching."""
    if input("Simulate Gale-Shapley load? (y/N): ").strip().lower() not in {"y", "yes"}:
        return None

    counts = {}
    for mode in COMMUTE_MODES:
        while True:
            try:
                value = int(input(f"Total {mode} commuters (including you if applicable): ") or "0")
                if value < 0:
                    raise ValueError
                counts[mode] = value
                break
            except ValueError:
                print("Enter a whole number of zero or more.")
    return counts

# --- Main Test Function ---
def run_route_test():
    """
    Runs a test of the routing engine for different commute modes,
    prints the results, and provides explanations for the chosen routes.
    """
    print("--- Starting Toxicity-Aware Routing Engine Test ---")

    source_coords, dest_coords, departure_time = get_user_input()
    if not source_coords or not dest_coords:
        return
    commuter_counts = get_commuter_counts()

    # Convert coordinates to UTM
    source_utm = to_utm(source_coords[0], source_coords[1])
    dest_utm = to_utm(dest_coords[0], dest_coords[1])

    print(f"Source (WGS84): {source_coords}")
    print(f"Destination (WGS84): {dest_coords}")
    print(f"Source (UTM): {source_utm}")
    print(f"Destination (UTM): {dest_utm}")
    if departure_time:
        print(f"Departure Time: {departure_time}")
    print("\n")

    for mode in COMMUTE_MODES:
        print(f"--- Testing Commute Mode: {mode.upper()} ---")

        # Prepare the request payload
        payload = {
            "origin": [source_coords[0], source_coords[1]],
            "destination": [dest_coords[0], dest_coords[1]],
            "mode": mode,
            "route_model": "stpignn",
        }
        if departure_time:
            payload["departure_time"] = departure_time
        if commuter_counts is not None:
            payload["commuter_counts"] = commuter_counts

        try:
            # Make the request to the routing API
            # TestClient creates an isolated app with its fallback graph.
            # Query the running service so every mode uses the live route state.
            response = requests.post(API_URL, json=payload, timeout=60)
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json()

            # --- Print Results ---
            print(f"Recommended Route ID: {data.get('stable_corridor_id')}")
            print(f"Total Cost (Toxicity Dose): {data.get('total_cost_w')}")
            if data.get("matching_applied"):
                print(f"Gale-Shapley cohort: {data.get('simulated_commuter_counts')}")
                print(f"Road-based route capacities: {data.get('route_capacities')}")
            else:
                print("Gale-Shapley load simulation: off (using this mode's top-ranked route)")

            recommended_route = None
            for candidate in data.get("candidates", []):
                if candidate.get("recommended"):
                    recommended_route = candidate
                    break
            
            if not recommended_route:
                print("No recommended route found in candidates.")
                continue
            
            print(f"Distance Covered: {recommended_route.get('distance_m')} meters\n")

            # --- Route Explanation ---
            print("--- Route Explanation ---")
            explanation = recommended_route.get("explanation", {})
            
            # Gale-Shapley and A* explanation
            score_exp = explanation.get("route_score", {})
            if score_exp:
                print("Gale-Shapley and A* Scoring (Preference Score):")
                print(f"  - Base Score: {score_exp.get('base_score')}")
                print(f"  - Dose Contribution: {score_exp.get('dose_contribution')}")
                print(f"  - Distance Contribution: {score_exp.get('distance_contribution')}")
                print(f"  - Final Score: {score_exp.get('final_score')}")
                print("  (This is the raw preference score used to rank candidates. A lower score is better for ranking, but the final stable corridor can differ after Gale-Shapley matching.)\n")

            # ST-PIGNN Captum Integrated Gradients Explanation
            neural_exp = explanation.get("neural_model", {})
            if neural_exp and neural_exp.get("available"):
                print("ST-PIGNN Integrated Gradients Explanation (Feature Importance):")
                print(f"  Method: {neural_exp.get('method')}")
                attributions = neural_exp.get("feature_attributions", {})
                if attributions:
                    for feature, value in sorted(attributions.items(), key=lambda item: abs(item[1]), reverse=True):
                        print(f"  - {feature}: {value:.4f}")
                else:
                    print("  - No feature attributions available.")
                print(f"  Reason: {neural_exp.get('reason')}\n")
            else:
                print("ST-PIGNN Integrated Gradients explanation not available for this route.\n")

            # Nodes changed explanation
            print("--- Node Analysis & Gale-Shapley Candidates ---")
            print(f"The recommended route ({recommended_route.get('id')}) consists of {len(recommended_route.get('node_ids', []))} nodes.")
            print("This path was chosen by the A* algorithm using a composite weight of distance and predicted toxicity from the ST-PIGNN model.")
            print("The Gale-Shapley algorithm then selected this route from a set of candidates to mitigate herd behavior.\n")

            if recommended_route.get("preference_rank", 0) > 1:
                print(
                    "Note: the recommended route is not the raw rank-1 candidate. "
                    "That is expected when the stable matcher reallocates commuters to respect route capacities and segment preferences.\n"
                )
            
            print("All evaluated candidates:")
            for cand in data.get("candidates", []):
                rec_marker = " (Recommended)" if cand.get('recommended') else ""
                print(f"  - Candidate: {cand.get('id')}{rec_marker}")
                print(f"    - Rank: {cand.get('preference_rank')}")
                print(f"    - Distance: {cand.get('distance_m')}m")
                print(f"    - Dose: {cand.get('dose_ug')}")


        except requests.exceptions.RequestException as e:
            print(f"Error calling routing API for mode '{mode}': {e}")
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON response for mode '{mode}'.")
        
        print("-" * 40 + "\n")

if __name__ == "__main__":
    run_route_test()
