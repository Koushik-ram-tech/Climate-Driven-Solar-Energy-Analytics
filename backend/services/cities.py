"""
Supported cities for the Solar GHI prediction model.
These correspond to the one-hot encoded CITY_* columns in the feature list.
"""

SUPPORTED_CITIES = [
    "Ahmedabad",
    "Bengaluru",
    "Bhopal",
    "Bhubaneswar",
    "Chandigarh",
    "Chennai",
    "Delhi",
    "Guwahati",
    "Hyderabad",
    "Jaipur",
    "Kochi",
    "Kolkata",
    "Mangalore",
    "Mumbai",
    "Pune",
]

# Map city name → one-hot column name as used in feature_list
CITY_COLUMN_MAP: dict[str, str] = {city: f"CITY_{city}" for city in SUPPORTED_CITIES}
