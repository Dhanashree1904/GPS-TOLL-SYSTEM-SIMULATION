import random
import simpy
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
from shapely.ops import nearest_points
from geopy.distance import geodesic
from tollcalc import calculate_toll

# Load the prepared data from GeoPackage files
def load_data():
    roads_df = gpd.read_file('roads.gpkg', layer='roads')
    tolls_df = gpd.read_file('tolls.gpkg', layer='tolls')
    points_df = gpd.read_file('points.gpkg', layer='points')
    return roads_df, tolls_df, points_df

def nearest_road(point, roads_df):
    """Find the nearest road to the given point."""
    min_dist = float('inf')
    nearest_road = None
    for idx, road in roads_df.iterrows():
        p1, p2 = nearest_points(point, road.geometry)
        dist = p1.distance(p2)
        if dist < min_dist:
            min_dist = dist
            nearest_road = road
    return nearest_road

def vehicle(env, vehicle_id, start_point, end_point, roads_df, tolls_df, bank_account, vehicle_data):
    """SimPy process representing a vehicle traveling from start_point to end_point."""
    print(f"Vehicle {vehicle_id} starting at {start_point['points']} at time {env.now}")

    current_point = Point(start_point.geometry.x, start_point.geometry.y)
    route = [current_point]
    total_distance = 0
    visited_roads = set()
    visited_tolls = set()

    toll_crossed = False
    toll_cost = 0

    while current_point != Point(end_point.geometry.x, end_point.geometry.y):
        road = nearest_road(current_point, roads_df)
        if road is None:
            print(f"Vehicle {vehicle_id} cannot find a road to travel on at point {current_point}")
            break
        if road['road'] not in visited_roads:
            print(f"Vehicle {vehicle_id} traveling on {road['road']} at time {env.now}")
            visited_roads.add(road['road'])
        
        route.append(road.geometry)
        travel_distance = geodesic((current_point.y, current_point.x), (road.geometry.coords[0][1], road.geometry.coords[0][0])).km
        total_distance += travel_distance
        current_point = Point(road.geometry.coords[-1])
        yield env.timeout(travel_distance / 10)  # Assuming average speed of 10 km/h

        for idx, toll in tolls_df.iterrows():
            if road.geometry.intersects(toll.geometry) and toll['toll'] not in visited_tolls:
                toll_cost, distance_to_toll = calculate_toll((current_point.y, current_point.x), (toll.geometry.centroid.y, toll.geometry.centroid.x))
                bank_account -= toll_cost
                toll_crossed = True
                visited_tolls.add(toll['toll'])
                print(f"Vehicle {vehicle_id} passing through {toll['toll']} at time {env.now}, toll cost: {toll_cost:.2f}, remaining balance: {bank_account:.2f}")
                vehicle_data.append({
                    'car_id': vehicle_id,
                    'start_position': start_point['points'],
                    'end_position': end_point['points'],
                    'balance': bank_account,
                    'toll': toll['toll'],
                    'toll_charges': toll_cost,
                    'distance_to_toll': distance_to_toll
                })

    if not toll_crossed:
        vehicle_data.append({
            'car_id': vehicle_id,
            'start_position': start_point['points'],
            'end_position': end_point['points'],
            'balance': bank_account,
            'toll': 'No toll zone crossed',
            'toll_charges': 0,
            'distance_to_toll': total_distance
        })

    print(f"Vehicle {vehicle_id} reached {end_point['points']} at time {env.now}")
    print(f"Vehicle {vehicle_id} end location: {end_point['points']}")

def main():
    # Load the prepared data
    roads_df, tolls_df, points_df = load_data()

    # Initialize the SimPy environment
    env = simpy.Environment()

    # Number of vehicles to simulate
    num_vehicles = 1

    # Bank account balance for each vehicle
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
