import pandas as pd
import requests
from io import StringIO
import os

cities = {
    "Bengaluru": (12.9716, 77.5946),
    "Chennai": (13.0827, 80.2707),
    "Hyderabad": (17.3850, 78.4867),
    "Kochi": (9.9312, 76.2673),
    "Mangalore": (12.9141, 74.8560),
    "Mumbai": (19.0760, 72.8777),
    "Pune": (18.5204, 73.8567),
    "Ahmedabad": (23.0225, 72.5714),
    "Delhi": (28.6139, 77.2090),
    "Chandigarh": (30.7333, 76.7794),
    "Jaipur": (26.9124, 75.7873),
    "Kolkata": (22.5726, 88.3639),
    "Bhubaneswar": (20.2961, 85.8245),
    "Bhopal": (23.2599, 77.4126),
    "Guwahati": (26.1445, 91.7362)
}

parameters = (
    "T2M,"
    "T2M_MAX,"
    "T2M_MIN,"
    "RH2M,"
    "PS,"
    "WS10M,"
    "CLOUD_AMT,"
    "PRECTOTCORR,"
    "ALLSKY_SFC_SW_DWN"
)

os.makedirs("data/raw", exist_ok=True)

for city, (lat, lon) in cities.items():

    url = (
        f"https://power.larc.nasa.gov/api/temporal/daily/point?"
        f"parameters={parameters}"
        f"&community=RE"
        f"&longitude={lon}"
        f"&latitude={lat}"
        f"&start=20190101"
        f"&end=20241231"
        f"&format=CSV"
    )

    print(f"Downloading {city}...")

    response = requests.get(url)

    file_path = f"data/raw/{city}.csv"

    with open(file_path, "wb") as f:
        f.write(response.content)

    print(f"Saved: {file_path}")

print("All downloads complete.")