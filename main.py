import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import streamlit as st
from iso3166 import countries


# Load Data
@st.cache_data
def load_data():
    df_data = pd.read_csv('Space+Missions+(start)/mission_launches.csv')
    df_data['Date'] = pd.to_datetime(df_data['Date'], errors='coerce')
    print(df_data.dtypes)

    df_data['Country'] = df_data['Location'].str.split(', ').str[-1]
    update = {
        'Russia': 'Russian Federation',
        'New Mexico': 'USA',
        'Yellow Sea': 'China',
        'Shahrud Missile Test Site': 'Iran, Islamic Republic of',
        'Pacific Missile Range Facility': 'USA',
        'Barents Sea': 'Russian Federation',
        'Gran Canaria': 'USA',
        'Marshall Islands': 'USA',
        'Iran': 'Iran, Islamic Republic of',
        'North Korea': "Korea, Democratic People's Republic of",
        'South Korea': "Korea, Republic of",
        'United Kingdom': 'United Kingdom of Great Britain and Northern Ireland',
        'Pacific Ocean': 'USA'
    }
    df_data['Country'] = df_data['Country'].replace(update)
    df_data['Country Code'] = df_data['Country'].apply(lambda x: (countries.get(x).alpha3))
    return df_data


df_data = load_data()

# Title and description
st.title("Space Mission Launches Analysis")
st.write("This app analyzes space mission launches over time, by country, organization, and other dimensions.")

# Dropdown menu to select which analysis to show
analysis_options = [
    "Number of Launches by Organisation",
    "Number of Launches by Country (Choropleth)",
    "Launches Over Time (Yearly and Monthly)",
    "Mission Success and Failures",
    "Cold War Space Race: USA vs USSR",
    "Top Organization per Year",
    "Mission Failures Over Time"
]
selected_analysis = st.selectbox("Select Analysis", analysis_options)

if selected_analysis == "Number of Launches by Organisation":
    # Number of launches per organization
    no_of_launches_per_company = df_data['Organisation'].value_counts().reset_index()
    no_of_launches_per_company.columns = ['Organisation', 'Launches']

    st.write("### Number of Launches by Organisation")
    fig = px.bar(no_of_launches_per_company, x='Organisation', y='Launches', color='Organisation',
                 title="Number of Space Mission Launches by Organisation")
    fig.update_layout(xaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig)

elif selected_analysis == "Number of Launches by Country (Choropleth)":
    launches_by_country = df_data.groupby(['Country', 'Country Code']).size().reset_index(name='Launch Count')

    st.write("### Launches by Country (Choropleth Map)")
    fig = px.choropleth(
        launches_by_country,
        locations='Country Code',
        color='Launch Count',
        hover_name='Country',
        title="Number of Launches by Country",
        color_continuous_scale='twilight'
    )
    st.plotly_chart(fig)

elif selected_analysis == "Launches Over Time (Yearly and Monthly)":
    # Ensure 'Date' column is in datetime format
    df_data['Date'] = pd.to_datetime(df_data['Date'], errors='coerce')  # Convert to datetime and handle errors

    # Drop rows where Date could not be converted (optional, depending on data)
    df_data = df_data.dropna(subset=['Date'])

    # Yearly launches
    launches_per_year = df_data.groupby(df_data['Date'].dt.year).size()

    st.write("### Launches Over Time (Yearly)")

    plt.figure(figsize=(20, 6))
    plt.plot(launches_per_year, marker='o', linestyle='-', color='red')
    plt.xlabel('Year')
    plt.ylabel('Number of Launches')
    plt.title('Number of Launches per Year')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.xticks(launches_per_year.index, rotation=45)
    plt.margins(x=0)
    st.pyplot(plt)

    # Monthly launches
    st.write("### Launches Over Time (Monthly)")
    launches_month_on_month = df_data.groupby('Date').size().reset_index(name='Launch Count')
    launches_month_on_month['Rolling Average'] = launches_month_on_month['Launch Count'].rolling(30).mean()

    fig = px.line(launches_month_on_month, x='Date', y='Launch Count', title="Monthly Launches with Rolling Average")
    fig.add_scatter(x=launches_month_on_month['Date'], y=launches_month_on_month['Rolling Average'], mode='lines',
                    name='Rolling Average')
    st.plotly_chart(fig)

elif selected_analysis == "Mission Success and Failures":
    # Ensure 'Date' column is in datetime format
    df_data['Date'] = pd.to_datetime(df_data['Date'], errors='coerce')  # Convert to datetime and handle errors

    # Drop rows where Date could not be converted (optional, depending on data)
    df_data = df_data.dropna(subset=['Date'])

    # Mission success/failure
    successful_missions = len(df_data[df_data['Mission_Status'] == 'Success'])
    failed_missions = len(df_data[df_data['Mission_Status'] == 'Failure'])

    st.write(f"### Number of Successful Missions: {successful_missions}")
    st.write(f"### Number of Failed Missions: {failed_missions}")

    # Mission status year-on-year
    mission_status_year_on_year = df_data.groupby(
        [df_data['Date'].dt.year.rename('Year'), 'Mission_Status']).size().reset_index(name='Total')

    mission_failures_year_on_year = mission_status_year_on_year[
        mission_status_year_on_year['Mission_Status'] == 'Failure']

    st.write("### Mission Failures Year-on-Year")
    plt.figure(figsize=(20, 6))
    plt.plot(mission_failures_year_on_year['Year'], mission_failures_year_on_year['Total'], marker='o', linestyle='-')
    plt.xlabel('Year')
    plt.ylabel('Mission Failures')
    plt.title('Total Number of Mission Failures Year on Year')
    plt.grid(True)
    st.pyplot(plt)


elif selected_analysis == "Cold War Space Race: USA vs USSR":
    cold_war_update = {
        'Russian Federation': 'USSR',
        'Kazakhstan': 'USSR'
    }

    # Convert 'Date' column to datetime format
    df_data['Date'] = pd.to_datetime(df_data['Date'], errors='coerce')

    # Filter out rows where 'Date' could not be converted
    df_data = df_data.dropna(subset=['Date'])

    # Ensure 'Country' values are not NaN before replacement
    df_data['Country'] = df_data['Country'].fillna('Unknown')

    # Replace 'Country' with 'USSR' for relevant countries before 1991
    df_data.loc[df_data['Date'].dt.year <= 1991, 'Country'] = df_data['Country'].replace(cold_war_update)

    # Filter data for years before or in 1991
    cold_war = df_data[df_data['Date'].dt.year <= 1991]

    # Group by year and country to get launch counts
    cold_war_launches = cold_war.groupby([cold_war['Date'].dt.year.rename('Year'), 'Country']).size().reset_index(name='Launch Count')

    # Filter for USA and USSR launches
    cold_war_launches_USA_USSR = cold_war_launches.loc[cold_war_launches['Country'].isin(['USA', 'USSR'])]

    st.write("### Cold War Space Race: USA vs USSR")

    # Check if the DataFrame is empty
    if cold_war_launches_USA_USSR.empty:
        st.write("No data available for USA and USSR launches during the Cold War.")
    else:
        fig = px.pie(cold_war_launches_USA_USSR, values="Launch Count", names="Country",
                     title='Cold War Space Race Total Rocket Launches')
        st.plotly_chart(fig)


elif selected_analysis == "Top Organization per Year":
    # Convert 'Date' column to datetime format
    df_data['Date'] = pd.to_datetime(df_data['Date'], errors='coerce')

    # Filter out rows where 'Date' could not be converted
    df_data = df_data.dropna(subset=['Date'])  # This will remove any rows with NaT in 'Date'

    # Group by year and organization to get launch counts
    launches_top10_organizations = df_data.groupby(
        [df_data['Date'].dt.year.rename('Year'), 'Organisation']).size().reset_index(name='Launch Count')

    # Get the top 10 organizations based on total launches
    top10_organizations = launches_top10_organizations.groupby('Organisation')['Launch Count'].sum().sort_values(
        ascending=False).head(10).reset_index()

    # Merge to filter only top 10 organizations
    launches_top10_organizations = launches_top10_organizations.merge(top10_organizations['Organisation'],
                                                                      on='Organisation', how='inner')

    st.write("### Top 10 Organizations by Number of Launches Over Time")
    fig = px.bar(launches_top10_organizations, x="Year", y="Launch Count", color="Organisation")
    st.plotly_chart(fig)


elif selected_analysis == "Mission Failures Over Time":
    total_mission_status_year_on_year = df_data.groupby(df_data['Date'].dt.year.rename('Year')).size().reset_index(
        name='Total Missions')
    mission_failures_year_on_year = df_data[df_data['Mission_Status'] == 'Failure'].groupby(
        df_data['Date'].dt.year.rename('Year')).size().reset_index(name='Failures')
    mission_failures_year_on_year['Percentage'] = (mission_failures_year_on_year['Failures'] /
                                                   total_mission_status_year_on_year['Total Missions']) * 100

    st.write("### Percentage of Mission Failures Over Time")
    plt.figure(figsize=(20, 6))
    plt.plot(mission_failures_year_on_year['Year'], mission_failures_year_on_year['Percentage'], marker='o',
             linestyle='-')
    plt.xlabel('Year')
    plt.ylabel('Mission Failures (%)')
    plt.title('Percentage of Failures over Time')
    plt.grid(True)
    st.pyplot(plt)

