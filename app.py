import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import folium_static

# Streamlit configuration
st.set_page_config(
    page_title='Aadhaar centers in India',
    page_icon='💳'
)

# Page title
st.header('Aadhaar centers in India by state')

# Load Aadhaar centers data
aadhar_centers_gdf = gpd.read_file('aadhar_centers/aadhar_centers_processed.shp')

# Load boundary data (India districts)
boundary_data = gpd.read_file('boundary_data/india_district_boundary_processed.shp')

# Dynamic generation of states_list and sorting
states_list = sorted(aadhar_centers_gdf['state'].unique().tolist())

# Dropdown to select a state
selected_state = st.selectbox('Select a state:', [None] + states_list)  # Add None as an option

if selected_state:

    # Filter Aadhaar centers for the selected state
    selected_aadhar_centers_gdf = aadhar_centers_gdf[
        aadhar_centers_gdf['state'] == selected_state
    ]

    st.write(f'Aadhaar centers in {selected_state} - {selected_aadhar_centers_gdf.shape[0]} existing centers')

    # Check for NaN values in latitude and longitude columns
    selected_aadhar_centers_gdf = selected_aadhar_centers_gdf.dropna(subset=['lat', 'long'])

    # Get the bounds of the selected state from boundary_data (case-insensitive)
    selected_state_bounds = boundary_data[
        boundary_data['STATE'] == selected_state
    ].total_bounds

    # Create a Folium map focused on the selected state
    m = folium.Map(
        location=[selected_aadhar_centers_gdf['lat'].mean(), selected_aadhar_centers_gdf['long'].mean()],
        zoom_start=6,
    )

    # Plot boundary_data on the map (only the boundary of the selected state)
    folium.GeoJson(
        boundary_data[boundary_data['STATE'] == selected_state],
        style_function=lambda x: {'color': 'red', 'weight': 2}
    ).add_to(m)

    # Plot Aadhaar centers on the map
    for idx, row in selected_aadhar_centers_gdf.iterrows():
        folium.Marker([row['lat'], row['long']], popup=row['gid'], tooltip=row['gid']).add_to(m)

    # Fit the map bounds to the selected state
    m.fit_bounds([[selected_state_bounds[1], selected_state_bounds[0]],
                  [selected_state_bounds[3], selected_state_bounds[2]]])

else:
    # Create a Folium map showing the entire boundary_data
    m = folium.Map(
        location=[aadhar_centers_gdf['lat'].mean(), aadhar_centers_gdf['long'].mean()],
        tiles='https://map1.vis.earthdata.nasa.gov/wmts-webmerc/VIIRS_CityLights_2012/default/GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpg',
        attr='Imagery provided by services from the Global Imagery Browse Services (GIBS), operated by the NASA/GSFC/Earth Science Data and Information System (<a href="https://earthdata.nasa.gov">ESDIS</a>) with funding provided by NASA/HQ.',
        zoom_start=6,
        max_zoom=8
    )

    # Plot boundary_data on the map
    # folium.GeoJson(boundary_data).add_to(m)

    # Fit bounds to the entire boundary_data
    m.fit_bounds([[boundary_data.total_bounds[1], boundary_data.total_bounds[0]],
                  [boundary_data.total_bounds[3], boundary_data.total_bounds[2]]])

# Display the Folium map using streamlit
folium_static(m)

# Footer
st.markdown(
    """
    <hr style="border:0.5px solid #e6e6e6">
    <p style="font-size: 80%; color: #808080; text-align: center;">
    Made with ❤️ by <a href="https://github.com/D3v1s0m" target="_blank">Team Arceus</a>
    </p>
    """,
    unsafe_allow_html=True
)