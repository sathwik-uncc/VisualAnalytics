#VA Final Project Group 6
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import altair as alt

DATE_TIME = "date/time"
DATA_URL = (
    "Motor_Vehicle_Collisions_2012-2021_v1.csv"
)

st.title("NYC Vehicular Accidents 2012-2021 Trends")
st.markdown("A project by Group 6")


@st.cache(persist=True)
def load_data(nrows):
    df = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH DATE', 'CRASH TIME']])
    df.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    lowercase = lambda x: str(x).lower()
    df.rename(lowercase, axis="columns", inplace=True)
    df.rename(columns={"crash date_crash time": "date/time"}, inplace=True)
    return df

data = load_data(1000000)


if st.sidebar.checkbox('Visualize on NYC Map'):
    st.header("Select the fields you want to visualize")
    select = st.selectbox('Fields', ['Number of people killed', 'Number of people injured'])
    keyword = ''
    if select == 'Number of people killed':
        keyword = 'killed'
    elif select == 'Number of people injured':
        keyword = 'injured'

    st.header("Where are the most people {} in NYC?".format(keyword))
    affected_people = st.slider("Number of people " + keyword + " in vehicle collisions", 0, int(data['number of persons '+keyword].max()))
    st.map(data.query("`number of persons "+keyword+"` >= @affected_people")[["latitude", "longitude"]].dropna(how="any"))

    st.header("How many collisions occur during a given time of day?")
    hour = st.slider("Hour to look at", 0, 23)
    data = data[data[DATE_TIME].dt.hour == hour]
    st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour, (hour + 1) % 24))

    mid_point = (np.average(data["latitude"]), np.average(data["longitude"]))

    st.write(pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state={
                "latitude": mid_point[0],
                "longitude": mid_point[1],
                "zoom": 11,
                "pitch": 50,
            },
            layers=[
                pdk.Layer(
                "HexagonLayer",
                data=data[['date/time', 'latitude', 'longitude']],
                get_position=["longitude", "latitude"],
                auto_highlight=True,
                radius=100,
                extruded=True,
                pickable=True,
                elevation_scale=4,
                elevation_range=[0, 1000],
                ),
            ],
        ))

    if st.checkbox("Show raw data", False):
        st.subheader("Raw data by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))
        st.write(data)

    st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))
    hour_filtered = data[
        (data[DATE_TIME].dt.hour >= hour) & (data[DATE_TIME].dt.hour < (hour + 1))
    ]
    histogram = np.histogram(hour_filtered[DATE_TIME].dt.minute, bins=60, range=(0, 60))[0]
    chart_data = pd.DataFrame({"minute": range(60), "crashes": histogram})

    fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
    st.write(fig)

    st.header("Top 5 dangerous streets by affected class")
    select = st.selectbox('Affected class', ['Pedestrians', 'Cyclists', 'Motorists'])

    if select == 'Pedestrians':
        st.write(data.query("`number of pedestrians "+keyword+"` >= 1")[["on street name", "number of pedestrians "+keyword]].sort_values(by=['number of pedestrians '+keyword], ascending=False).dropna(how="any")[:20])

    elif select == 'Cyclists':
        st.write(data.query("`number of cyclist "+keyword+"` >= 1")[["on street name", "number of cyclist "+keyword]].sort_values(by=['number of cyclist '+keyword], ascending=False).dropna(how="any")[:20])

    else:
        st.write(data.query("`number of motorist "+keyword+"` >= 1")[["on street name", "number of motorist "+keyword]].sort_values(by=['number of motorist '+keyword], ascending=False).dropna(how="any")[:20])

if st.sidebar.checkbox('Bar graph visualizations'): 
    #Bar graphs for Top 5 Contributing factors and types of vehicles and streets
    col_list=["VEHICLE TYPE CODE 1","CONTRIBUTING FACTOR VEHICLE 1","ON STREET NAME"]
    new_data=pd.read_csv(DATA_URL, usecols=col_list)
    st.header("Top 5 Vehicle Types and Contributing Factors causing accidents, Streets of occurances")
    #Types of vehicles count
    veh_counts= new_data['VEHICLE TYPE CODE 1'].value_counts()
    vehcount_df=pd.DataFrame(veh_counts)
    vehcount_df = vehcount_df.reset_index()
    vehcount_df.columns = ['Vehicle Types', 'Accidents Count']
    veh_five=vehcount_df.loc[[0,1,2,3,4]]
    # Types of contributing factors
    factors_counts= new_data['CONTRIBUTING FACTOR VEHICLE 1'].value_counts()
    factors_counts_df=pd.DataFrame(factors_counts)
    factors_counts_df = factors_counts_df.reset_index()
    factors_counts_df.columns = ['Contributing Factors', 'Accidents Count']
    factors_five=factors_counts_df.loc[[1,2,3,4,5]]
    #Street names
    street_counts= new_data['ON STREET NAME'].value_counts()
    street_counts_df=pd.DataFrame(street_counts)
    street_counts_df = street_counts_df.reset_index()
    street_counts_df.columns = ['Street Names', 'Accidents Count']
    streets_five=street_counts_df.loc[[0,1,2,3,4]]
    #Dropdown menu
    options = st.selectbox('Select Top 5 Category', ['Vehicle Types', 'Contributing Factors','Street Names'])

    if options == 'Vehicle Types':
        fig_contrib=px.bar(veh_five, x= 'Vehicle Types', y='Accidents Count')
        st.write(fig_contrib)

    elif options == 'Contributing Factors':
        fig_contrib=px.bar(factors_five, x= 'Contributing Factors', y='Accidents Count')
        st.write(fig_contrib)

    else:
        fig_contrib=px.bar(streets_five, x= 'Street Names', y='Accidents Count')
        st.write(fig_contrib)

if st.sidebar.checkbox('Accidents per year'):
    Location = DATA_URL
    df1 = pd.read_csv(Location,index_col='COLLISION_ID') 
    df2 = df1[['CRASH DATE']]
    df2['NUMBER_OF_ACCIDENTS'] = 1
    df3 = df2.reset_index().groupby('CRASH DATE').sum()
    del df3['COLLISION_ID'] 
    df3['YEAR'] = pd.DatetimeIndex(df3.index).year
    df3['MONTH'] = pd.DatetimeIndex(df3.index).month 
    df3.sort_values(by = 'YEAR')
    cols = list(np.array(df3['YEAR'].unique()))
    
    option = st.multiselect('Which year do you want to display?', cols, cols[0])

    multi_lc = alt.Chart(df3).mark_line().encode(
        x= alt.X('MONTH:O',title = 'MONTHS'),
        y= alt.Y('sum(NUMBER_OF_ACCIDENTS):Q',title = 'NUMBER OF ACCIDENTS'),
        color='YEAR:O'
    ).transform_filter(
        alt.FieldOneOfPredicate(field='YEAR', oneOf=option)
    ).properties(
        title='Multiline Chart Visualization of NYC Accidents',
        width=1000,
        height=600
    ).interactive()
    st.write(multi_lc)
