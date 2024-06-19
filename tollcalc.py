from geopy.distance import geodesic
from datetime import datetime, timedelta

def calculate_toll(current_location, toll_location, current_time_float, bank_account):
    # Convert simulation time (float) to datetime
    start_time = datetime(2024, 6, 1, 0, 0, 0)  # Choose your simulation start time
    current_time = start_time + timedelta(hours=current_time_float)  # Assuming hours are your simulation time unit

    # Extract hour and day
    hour = current_time.hour
    day_of_week = current_time.weekday()  # Monday is 0 and Sunday is 6

    # Calculate distance between current_location and toll_location
    distance_km = geodesic(current_location, toll_location).kilometers

    # Example toll calculation logic based on hour and day_of_week
    toll_cost = distance_km * 6  # Default toll cost: 6 per km

    if 6 <= hour < 10 or 17 <= hour < 20:  # Morning and evening rush hour
        toll_cost *= 1.2  # Increase toll by 20%
    elif day_of_week >= 5:  # Weekend toll
        toll_cost *= 1.1  # Increase toll by 10%

    # Check if bank balance is zero and apply penalty (double toll)
    if toll_cost >=0 and toll_cost > bank_account:
        toll_cost *= 2

    return toll_cost, distance_km
