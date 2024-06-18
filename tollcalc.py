from geopy.distance import geodesic

def calculate_toll(start_coord, toll_coord):
   
    distance_km = geodesic(start_coord, toll_coord).kilometers
    toll_cost = distance_km * 6  # Assuming the cost is 6 per km
    return toll_cost, distance_km
