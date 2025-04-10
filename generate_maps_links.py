import webbrowser
from urllib.parse import quote

def generate_maps_link(origin, destination, waypoints=None):
    base_url = "https://www.google.com/maps/dir/"
    
    # Format origin and destination
    origin_formatted = quote(origin)
    destination_formatted = quote(destination)
    
    # Build URL
    url = f"{base_url}{origin_formatted}/{destination_formatted}"
    
    # Add waypoints if provided
    if waypoints:
        waypoints_formatted = "/".join(quote(point) for point in waypoints)
        url = f"{base_url}{origin_formatted}/{waypoints_formatted}/{destination_formatted}"
    
    return url

# Generate and test links for all routes
routes = [
    {
        "name": "Regular Route",
        "origin": "Kothapet, Hyderabad",
        "destination": "Nagole, Hyderabad",
        "waypoints": ["LB Nagar, Hyderabad"]
    },
    {
        "name": "Recommended Route 1",
        "origin": "Kothapet, Hyderabad",
        "destination": "Nagole, Hyderabad",
        "waypoints": ["Mohan Nagar, Hyderabad"]
    },
    {
        "name": "Alternative Route 2",
        "origin": "Kothapet, Hyderabad",
        "destination": "Nagole, Hyderabad",
        "waypoints": ["Dilsukhnagar, Hyderabad", "Chaitanyapuri, Hyderabad"]
    },
    {
        "name": "Alternative Route 3",
        "origin": "Kothapet, Hyderabad",
        "destination": "Nagole, Hyderabad",
        "waypoints": ["Hayathnagar, Hyderabad"]
    }
]

print("Generated Google Maps Links:")
print("==========================")
for route in routes:
    link = generate_maps_link(route["origin"], route["destination"], route["waypoints"])
    print(f"\n{route['name']}:")
    print(link) 