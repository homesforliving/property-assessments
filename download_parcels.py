import requests
import geopandas as gpd
import matplotlib.pyplot as plt

def download_properties():
    #print directory content of active directory
    # Base URL for the ArcGIS REST API
    base_url = "https://mapservices.crd.bc.ca/arcgis/rest/services/Properties/MapServer"
    layer_id = 3

    # Full URL for the query operation
    query_url = f"{base_url}/{layer_id}/query"

    # Query parameters
    params = {
        "where": "BCAJurisdiction IN ('317')",  # Oak Bay only
        #"where": "BCAJurisdiction IN ('234', '317', '307', '308', '309', '389')",  # Filter by jurisdiction
        "outFields": "*",  # Retrieve all fields
        "f": "geojson",  # Output format
        "resultRecordCount": 3000,  # Max records per request
    }

    # Initialize variables for pagination
    result_offset = 0
    all_features = []

    while True:
        # Update the resultOffset parameter for pagination
        params["resultOffset"] = result_offset

        # Send the query request
        response = requests.get(query_url, params=params)

        # Check if the request was successful
        if response.status_code != 200:
            print(f"Failed to fetch data. HTTP status code: {response.status_code}")
            print(response.text)
            break

        # Parse the GeoJSON response
        geojson_data = response.json()

        # Extract features
        features = geojson_data.get("features", [])
        all_features.extend(features)

        # Check if there are more records to fetch
        if len(features) < params["resultRecordCount"]:
            # If fewer records are returned, we’ve fetched everything
            break

        # Increment the offset for the next batch
        result_offset += params["resultRecordCount"]

    # Load all features into a GeoDataFrame
    if all_features:
        gdf = gpd.GeoDataFrame.from_features(all_features)
        
        gdf = gdf.set_crs(epsg=4326).to_crs(epsg=26910)

        #download to parcels/raw_download.geojson
        gdf.to_file("parcels/raw_download.geojson", driver='GeoJSON')
        print("All data retrieved")

        return
    
    else:
        print("No data retrieved.")

    return

def analyze():
    parcels = gpd.read_file("parcels/raw_download.geojson")

    parcels.plot()
    plt.show()


analyze()