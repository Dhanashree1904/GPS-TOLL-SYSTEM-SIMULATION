from flask import Flask, render_template, jsonify
import os
import pandas as pd
import folium

app = Flask(__name__)

# Load the vehicle data
vehicle_data_path = os.path.join(os.path.dirname(__file__), 'vehicle_data.csv')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/vehicle_data', methods=['GET'])
def get_vehicle_data():
    print(f"CSV file path: {vehicle_data_path}")  # Debugging line to print the file path
    if os.path.exists(vehicle_data_path):
        try:
            vehicle_data = pd.read_csv(vehicle_data_path)
            print(vehicle_data)  # Debugging line to print the data
            return jsonify(vehicle_data.to_dict(orient='records'))
        except pd.errors.EmptyDataError:
            print("CSV file is empty")
            return jsonify([])  # Return empty JSON array if the file is empty
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return jsonify([])  # Return empty JSON array on any other error
    else:
        print("vehicle_data.csv file not found")  # Debugging line
        return jsonify([])

@app.route('/simulation_map')
def simulation_map():
    # Example of creating a Folium map
    m = folium.Map(location=[51.5074, -0.1278], zoom_start=10)  # London coordinates

    # Example marker
    folium.Marker([51.5074, -0.1278], popup='London').add_to(m)

    # Save the map to HTML
    map_file_path = os.path.join(os.path.dirname(__file__), 'templates', 'map.html')
    m.save(map_file_path)

    return render_template('map.html')

if __name__ == "__main__":
    app.run(debug=True)


