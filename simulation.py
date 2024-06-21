import random
import simpy
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import nearest_points  # Ensure this line is included
from geopy.distance import geodesic
import os
from datetime import datetime, timedelta

# Assuming tollcalc.py contains the calculate_toll function
from tollcalc import calculate_toll

# Function to load data from GeoPackage files
def load_data():
    base_path = r'C:\Users\Admin\Desktop\Intel Project'  # Replace with your actual base directory path
    roads_path = os.path.join(base_path, 'roads.gpkg')
    tolls_path = os.path.join(base_path, 'tolls.gpkg')
    points_path = os.path.join(base_path, 'points.gpkg')

    try:
        roads_df = gpd.read_file(roads_path, layer='roads')
    except Exception as e:
        print(f"Error loading {roads_path}: {e}")
        return None, None, None

    try:
        tolls_df = gpd.read_file(tolls_path, layer='tolls')
    except Exception as e:
        print(f"Error loading {tolls_path}: {e}")
        return None, None, None

    try:
        points_df = gpd.read_file(points_path, layer='points')
    except Exception as e:
        print(f"Error loading {points_path}: {e}")
        return None, None, None

    return roads_df, tolls_df, points_df

# Function to find the nearest road to a given point
def nearest_road(point, roads_df):
    min_dist = float('inf')
    nearest_road = None
    for idx, road in roads_df.iterrows():
        p1, p2 = nearest_points(point, road.geometry)  # Ensure nearest_points is correctly imported
        dist = p1.distance(p2)
        if dist < min_dist:
            min_dist = dist
            nearest_road = road
    return nearest_road

# SimPy process representing a vehicle traveling
def vehicle(env, vehicle_id, start_point, end_point, roads_df, tolls_df, bank_account, vehicle_data):
    start_time = random.uniform(0, 24)  # Random start time between 0 and 24 hours
    print(f"Vehicle {vehicle_id} starting at {start_point['points']} at time {start_time:.2f}")

    current_point = Point(start_point.geometry.x, start_point.geometry.y)
    route = [current_point]
    total_distance = 0
    visited_roads = set()
    visited_tolls = set()
    road_start_time = start_time  # Track start time of the current road segment
    current_road = None
    last_toll_time = start_time  # Track the time when the last toll was passed

    while current_point != Point(end_point.geometry.x, end_point.geometry.y):
        road = nearest_road(current_point, roads_df)
        if road is None:
            print(f"Vehicle {vehicle_id} cannot find a road to travel on at point {current_point}")
            break
        
        if road['road'] != current_road:  # Check if road has changed
            if current_road is not None:
                print(f"Vehicle {vehicle_id} traveling on {current_road} for {start_time + env.now - road_start_time:.2f} hours at time {start_time + env.now:.2f}")
            current_road = road['road']
            road_start_time = start_time + env.now  # Update start time of new road segment

        route.append(road.geometry)
        travel_distance = geodesic((current_point.y, current_point.x), (road.geometry.coords[0][1], road.geometry.coords[0][0])).km
        total_distance += travel_distance
        current_point = Point(road.geometry.coords[-1])
        yield env.timeout(travel_distance / 10)  # Assuming average speed of 10 km/h

        # Check for tolls along the current road segment
        for idx, toll in tolls_df.iterrows():
            if road.geometry.intersects(toll.geometry) and toll['toll'] not in visited_tolls:
                toll_cost, distance_to_toll = calculate_toll((current_point.y, current_point.x), (toll.geometry.centroid.y, toll.geometry.centroid.x), start_time + env.now, bank_account)
                bank_account -= toll_cost
                visited_tolls.add(toll['toll'])
                time_difference = start_time + env.now - last_toll_time
                print(f"Vehicle {vehicle_id} passing through {toll['toll']} at time {start_time + env.now:.2f}, toll cost: {toll_cost:.2f}, time since last toll: {time_difference:.2f} hours, remaining balance: {bank_account:.2f}")
                last_toll_time = start_time + env.now  # Update last toll time
                vehicle_data.append({
                    'car_id': vehicle_id,
                    'start_position': start_point['points'],
                    'end_position': end_point['points'],
                    'balance': bank_account,
                    'toll': toll['toll'],
                    'toll_charges': toll_cost,
                    'distance_to_toll': distance_to_toll,
                    'passage_time': start_time + env.now,  # Record passage time for each toll
                    'road_travel_time': start_time + env.now - road_start_time  # Record road travel time
                })

    # Record the vehicle's journey end after passing all tolls
    if current_road is not None:
        print(f"Vehicle {vehicle_id} traveling on {current_road} for {start_time + env.now - road_start_time:.2f} hours at time {start_time + env.now:.2f}")
    print(f"Vehicle {vehicle_id} reached {end_point['points']} at time {start_time + env.now:.2f}")
    print(f"Vehicle {vehicle_id} end location: {end_point['points']}")
    vehicle_data.append({
        'car_id': vehicle_id,
        'start_position': start_point['points'],
        'end_position': end_point['points'],
        'balance': bank_account,
        'toll': 'No toll zone crossed',
        'toll_charges': 0,
        'distance_to_toll': total_distance,
        'passage_time': start_time + env.now,  # Record end time
        'road_travel_time': start_time + env.now - road_start_time  # Record final road travel time
    })


# Main simulation function
def main():
    # Load data from GeoPackage files
    roads_df, tolls_df, points_df = load_data()

    if roads_df is None or tolls_df is None or points_df is None:
        print("Error loading data. Exiting.")
        return

    # Initialize SimPy environment
    env = simpy.Environment()

    # Number of vehicles to simulate
    num_vehicles = 1

    # Initial bank account balance for each vehicle
    initial_balance = 500

    # Dataframe to save vehicle data
    vehicle_data = []

    # Create vehicle processes
    for i in range(num_vehicles):
        start_point = points_df.sample(random_state=random.randint(0, 1000)).iloc[0]
        end_point = points_df.sample(random_state=random.randint(0, 1000)).iloc[0]

        while start_point['points'] == end_point['points']:
            end_point = points_df.sample(random_state=random.randint(0, 1000)).iloc[0]

        env.process(vehicle(env, i, start_point, end_point, roads_df, tolls_df, initial_balance, vehicle_data))

    # Run the simulation
    env.run(until=100)  # Arbitrary simulation time

    # Save vehicle data to CSV
    vehicle_df = pd.DataFrame(vehicle_data)
    vehicle_df.to_csv('vehicle_data.csv', index=False)
    print("Vehicle data saved to vehicle_data.csv")

if __name__ == "__main__":
    main()


