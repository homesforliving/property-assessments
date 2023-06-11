import pandas as pd
import geopandas as gpd

import os
from inspect import getsourcefile
from os.path import abspath

import matplotlib.pyplot as plt

import plotly.express as px

#set active directory to file location
directory = abspath(getsourcefile(lambda:0))
#check if system uses forward or backslashes for writing directories
if(directory.rfind("/") != -1):
    newDirectory = directory[:(directory.rfind("/")+1)]
else:
    newDirectory = directory[:(directory.rfind("\\")+1)]
os.chdir(newDirectory)

def condense_property_gdf():

    #data from here: https://hub.arcgis.com/datasets/SIPP::crd-properties/explore?layer=3&location=48.440229%2C-123.278142%2C13.00
    properties = gpd.read_file("CRD_Properties.geojson")
    properties = properties[properties['geometry'].is_valid]
    
    properties['City'] = None
    
    #Each city has a jurisdiction code. 317 is Oak Bay, Esquimalt is 307, City of Victoria is 234, and Saanich is 308, 309, or 389

    #the relevant column is '"BCAJurisdiction' and stores data as text
    #Create a column called City and fill it with the appropriate city name
    def code_to_city(code):
        if code == '317':
            return 'OB'
        elif code == '307':
            return 'ES'
        elif code == '234':
            return 'VC'
        elif code in ['308', '309', '389']:
            return 'SN'
        return(None)
    
    properties['City'] = properties['BCAJurisdiction'].apply(code_to_city)

    properties = properties[properties['City'].isin(['VC', 'OB', 'ES', 'SN'])]
    properties = properties[['Folio', 'City', 'StreetName', 'StreetNumber', 'geometry']]
    properties['AddressCombined'] = properties['StreetNumber'].astype(str) + ' ' + properties['StreetName']
    properties.to_file("Core Properties.geojson", driver='GeoJSON')

    return

#condense_property_gdf()

year = 2023

victoria_assessments = pd.read_csv("Victoria/{} Victoria.csv".format(year)).drop_duplicates()
oak_bay_assessments = pd.read_csv("Oak Bay/{} Oak Bay.csv".format(year)).drop_duplicates()
saanich_assessments = pd.read_excel("Saanich/{} Saanich.xlsx".format(year)).drop_duplicates()
esquimalt_assessments = pd.read_excel("Esquimalt/{} Esquimalt.xlsx".format(year)).drop_duplicates()

properties = gpd.read_file("Core Properties.geojson")

properties = properties.dissolve(by="Folio").reset_index()

def plot(data):
    #convert to NAD zone 10n
    data = data.to_crs(epsg=26910)
    data['Area'] = data.geometry.area
    data['Total Value'] = data['Land Value'] + data['Improvement Value']
    data['Land Value per Area'] = (data['Land Value'] / data['Area']).round(0)
    data['Total Value per Area'] = (data['Total Value'] / data['Area']).round(0)
    data.Area = data.Area.round(0)

    data = data.to_crs(epsg=4326)
   
    fig = px.choropleth_mapbox(data, geojson=data.geometry, locations=data.index, color='Land Value per Area',
                            color_continuous_scale="Viridis",
                            range_color=(1000, 4000),
                            mapbox_style="carto-positron",
                            zoom=9, center = {"lat": 48.4284, "lon": -123.3656},
                            opacity=0.7,
                            custom_data=['AddressCombined', 'Area', 'Land Value', 'Total Value', 'Land Value per Area', 'Total Value per Area']
    )

    fig.update_traces(marker_line_width=.00,
                        hovertemplate = """
                        <b>%{customdata[0]}</b><br>
                        <b>Area: </b>%{customdata[1]} M2 <br>
                        <b>Land Value: </b>%{customdata[2]} $ <br>
                        <b>Total Value: </b>%{customdata[3]} $ <br>
                        <b>Land Value per M2: </b> %{customdata[4]} $/M2 <br>
                        <b>Total Value per M2: </b> %{customdata[5]} $/M2"""
                                                        )
        #remove margin around plot
                            
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    fig.write_html("Land Assessments.html")
    #fig.show()
    return

def oak_bay_data(properties, ob_assessments):

    properties = properties[properties['City'] == 'OB']
    
    properties.Folio = properties.Folio.str.split('.').str[1]

    ob_assessments['Land Value'] = ob_assessments['Actual Value Land Total']
    ob_assessments['Improvement Value'] = ob_assessments['Actual Value Impr Total']
    ob_assessments['Folio'] = ob_assessments['Roll Number (Formatted)']

    ob_assessments = ob_assessments[['Folio', 'Land Value', 'Improvement Value']]

    merged_assessments = ob_assessments.merge(properties, left_on='Folio', right_on='Folio', how='left')

    #convert merged_assessments to geodataframe
    merged_assessments = merged_assessments[['City', 'AddressCombined', 'StreetName', 'StreetNumber', 'Land Value', 'Improvement Value', 'geometry']]
    merged_assessments = gpd.GeoDataFrame(merged_assessments, geometry='geometry')

    print("There are {} properties in Oak Bay".format(len(merged_assessments)))

    return(merged_assessments)

def saanich_data(properties, saanich_assessments):

    properties = properties[properties['City'] == 'SN']

    properties['Folio'] = properties['Folio'].str[-11:]

    saanich_assessments['Land Value'] = saanich_assessments['Assess Land Exempt Amt']
    saanich_assessments['Improvement Value'] = saanich_assessments['Assess Improvement Exempt Amt']
    saanich_assessments = saanich_assessments[['Folio', 'Land Value', 'Improvement Value']]

    merged_assessments = saanich_assessments.merge(properties, left_on='Folio', right_on='Folio', how='left')

    #convert merged_assessments to geodataframe
    merged_assessments = merged_assessments[['City', 'AddressCombined', 'StreetName', 'StreetNumber', 'Land Value', 'Improvement Value', 'geometry']]
    merged_assessments = gpd.GeoDataFrame(merged_assessments, geometry='geometry')

    print("There are {} properties in Saanich".format(len(merged_assessments)))

    return(merged_assessments)

def victoria_data(properties, victoria_assessments):
   
    properties = properties[properties['City'] == 'VC']

    victoria_assessments = victoria_assessments[victoria_assessments['assess_type'] == 'GENERAL']
    victoria_assessments['FOLIO'] = victoria_assessments['FOLIO'].astype(str)

    victoria_assessments['Land Value'] = victoria_assessments['land_gross'].copy()
    victoria_assessments['Improvement Value'] = victoria_assessments['impr_gross'].copy()

    properties.Folio = properties.Folio.str.split('.').str[1]
    properties.Folio = properties.Folio.str.replace('-', '')

    def add_zeroes(folio):
        if len(folio) < 8:
            return '0' + folio
        else:
            return folio

    victoria_assessments.FOLIO = victoria_assessments.FOLIO.apply(add_zeroes)
    victoria_assessments = victoria_assessments[['FOLIO', 'Land Value', 'Improvement Value']]

    merged_assessments = victoria_assessments.merge(properties, left_on='FOLIO', right_on='Folio', how='left')

    merged_assessments = merged_assessments[['City', 'AddressCombined', 'StreetName', 'StreetNumber', 'Land Value', 'Improvement Value', 'geometry']]
    merged_assessments = gpd.GeoDataFrame(merged_assessments, geometry='geometry')

    print("There are {} properties in Victoria".format(len(merged_assessments)))

    return(merged_assessments)

#victoria_data(properties.copy(), victoria_assessments.copy())
#saanich_data(properties, saanich_assessments)

def analyze():
    vic = victoria_data(properties.copy(), victoria_assessments.copy())
    san = saanich_data(properties.copy(), saanich_assessments.copy())
    ob = oak_bay_data(properties.copy(), oak_bay_assessments.copy())

    merged_assessments = pd.concat([vic, san, ob])
    merged_assessments = gpd.GeoDataFrame(merged_assessments, geometry='geometry')

    #print length
    print("There are {} properties in Victoria , OB, and Saanich with data".format(len(merged_assessments)))

    #select rows where StreetName and StreetNumber are not null or blank
    properties_with_complete_addresses = merged_assessments[merged_assessments['StreetName'].notna() & merged_assessments['StreetNumber'].notna()]

    #select rows where StreetName and StreetNumber are null or blank
    properties_with_incomplete_addresses = merged_assessments[merged_assessments['StreetName'].isna() | merged_assessments['StreetNumber'].isna()]

    #dissolve properties with complete addresses by AddressCombined, aggregate all other columns as sum
    properties_with_complete_addresses = properties_with_complete_addresses.dissolve(by='AddressCombined', aggfunc='sum').reset_index()

    #concatenate properties with complete addresses and properties with incomplete addresses

    merged_assessments = pd.concat([properties_with_complete_addresses, properties_with_incomplete_addresses])
    merged_assessments = gpd.GeoDataFrame(merged_assessments, geometry='geometry')

    print(merged_assessments)

    print("Dissolved by Address. There are now {} properties in Victoria, OB and Saanich".format(len(merged_assessments)))
    
    plot(merged_assessments)
    return

analyze()
