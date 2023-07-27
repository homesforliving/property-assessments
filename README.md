# Property-Assessments
Property assessments for municipalities throughout the CRD, obtained from open data portals and FOI requests. So far we have Victoria, Esquimalt, Oak Bay, and Saanich. If you get a hold of data for different munis or years, feel free to add it to this repo!

`mapping.py` combines the different sources of data, along with a dataset of property boundaries, to create a harmonized map of per M2 property values for the CRD.

**A note of caution**
First, land values != tax revenue.

Second, I make no representation of the accuracy of this data or of the map created using it. It's always good to cross-reference data with [BC Asssessment](https://www.bcassessment.ca/?sp=1&act=). If you find any bugs, please let me know or submit a pull request! Consider this map a first draft.

##Links

View the map in its current state: homesforliving.github.io/
Properties dataset: [here](https://hub.arcgis.com/datasets/SIPP::crd-properties/explore?layer=3&location=48.440229%2C-123.278142%2C13.00)

Go to the 'data' folder in this repo for the underlying data.

##Getting Started
First, download the property geojson from the link above (it's ~300mb). Then, run `condense_property_gdf` to simplify the data to the core munis (Victoria, Esquimalt, Oak Bay, Saanich). This will save a new geojson to the data folder. Once you've done this, you can run `analyze` to merge the different data sources together and create the map.
