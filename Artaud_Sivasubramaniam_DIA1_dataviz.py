import pandas as pd
import streamlit as st
import pycountry_convert as pc 
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp
from geopy.geocoders import Nominatim

df = pd.read_csv("Life Expectancy Data.csv")

########## Creation of a new column continent ##########

# With the library pycountry_convert we are going to create a new column "Continent" that will correspond to the continent of the country.

continent_name = {
    'AF': 'Africa',
    'AS': 'Asia',
    'EU': 'Europe',
    'NA': 'North America',
    'OC': 'Oceania',
    'SA': 'South America',
    'AN': 'Antarctica'
}

# Replacing the special cases
df['Country'] = df['Country'].replace({'Bolivia (Plurinational State of)': 'Bolivia', 'Iran (Islamic Republic of)': 'Iran', 'Micronesia (Federated States of)':'Micronesia','Republic of Korea':'Korea, Republic of', 'Korea':"Korea (Democratic People's Republic of)",'The former Yugoslav republic of Macedonia':'North Macedonia','Venezuela (Bolivarian Republic of)':'Venezuela'})

def convert(row):
    # convert country name to country code
    country_code =pc.country_name_to_country_alpha2(row.Country,cn_name_format="default")
    # convert country_code to continent code
    try:
        continent_code = pc.country_alpha2_to_continent_code(country_code)
        return continent_name.get(continent_code, None)
    except :
        return None

df['Continent'] = df.apply(convert,axis=1)

########## Creation of a new columns longitude and latitude ##########

unique_countries = pd.DataFrame(df['Country'].unique(), columns=['Country'])
geolocator = Nominatim(user_agent="my_geocoder")

def get_lat_lon(country):
    location = geolocator.geocode(country, timeout=5)
    if location:
        return pd.Series({'latitude': location.latitude, 'longitude': location.longitude})
    else:
        return pd.Series({'latitude': None, 'longitude': None})

unique_countries[['latitude', 'longitude']] = unique_countries['Country'].apply(get_lat_lon)
df = pd.merge(df, unique_countries, on='Country', how='left')

########## 1. Average life expectancy and population over the years ##########

average_life_expectancy_yearly = df.groupby('Year')['Life expectancy '].mean().reset_index()
average_population_yearly = df.groupby('Year')['Population'].mean().reset_index()

fig1 = sp.make_subplots(rows=2, cols=1, subplot_titles=['Average Life Expectancy', 'Average Population'])

fig1.add_trace(
    go.Scatter(x=average_life_expectancy_yearly['Year'], y=average_life_expectancy_yearly['Life expectancy '],
               mode='lines', name='Life Expectancy'),
    row=1, col=1
)

fig1.add_trace(
    go.Scatter(x=average_population_yearly['Year'], y=average_population_yearly['Population'],
               mode='lines', name='Population'),
    row=2, col=1
)

fig1.update_layout(
    font=dict(size=12),
    width=1500,
    height=600,
    margin=dict(l=20, r=20, t=60, b=20),
)

st.plotly_chart(fig1, use_container_width=True)

########## 2. Life Expectancy over the years of the top 10 and bottom 10 countries ##########

average_life_expectancy = df.groupby('Country')['Life expectancy '].mean().reset_index() # calcultae the average life expectancy
top10_countries = average_life_expectancy.nlargest(5, 'Life expectancy ') # take the top 10 average life expectancy
bottom10_countries = average_life_expectancy.nsmallest(5, 'Life expectancy ') # take the bottom 10 average life expectancy

# Filtering the Original DataFrame for the Selected Countries
selected_countries = top10_countries['Country'].tolist() + bottom10_countries['Country'].tolist()
filtered_df = df[df['Country'].isin(selected_countries)]

fig2 = px.line(filtered_df, x='Year', y='Life expectancy ', color='Country',title='Life Expectancy Over the Years for the top 5 and bottom 5 Selected Countries')
fig2.update_layout(
    xaxis_title='Year',
    yaxis_title='Life Expectancy',
    legend_title='Country',
    font=dict(size=15),
    width=1500,
    height=1000,
    margin=dict(l=20, r=20, t=60, b=20))

st.plotly_chart(fig2, use_container_width=True)

########## 3. Violin Plot for Life Expectancy by Continent ##########

fig3 = px.violin(df, x='Continent', y='Life expectancy ', color='Continent', box=True, title='Violin Plot for Life Expectancy and Population by Continent')

fig3.update_layout(
    xaxis_title='Continent',
    yaxis_title='Life Expectancy',
    legend_title='Continent',
    font=dict(size=12),
    width=1500,
    height=1000,
    margin=dict(l=20, r=20, t=60, b=20),
)

st.plotly_chart(fig3, use_container_width=True)

########## 4. Pie chart for the distribution of countries by Status ##########

fig4 = px.pie(
    df, 
    names='Status', 
    title='Distribution of Countries by Development Status',
    color='Status',  # Assigning colors based on the 'Status' column
    color_discrete_sequence=['#67001F', '#F4A582'],
    hole=0.4, 
)

# Update layout for better readability
fig4.update_layout(
    width=1500,
    height=1000,
    legend_title_text='Development Status',
)

st.plotly_chart(fig4, use_container_width=True)

########## 5. Comparing the GDP from 2000 to 2015 by the status ##########

df_gdp_avg=df.groupby(['Year', 'Status'])['GDP'].mean().reset_index()

fig5 = px.bar(df_gdp_avg, x='Status', y='GDP', color='Status', title='Average GDP by Country Status Over Years',animation_frame='Year', barmode='group')
fig5.update_layout(xaxis_title='Year', yaxis_title='Average GDP (USD)', width=1200, height=800)

st.plotly_chart(fig5, use_container_width=True)

########## 6. Comparing the life expectancy from 2000 to 2015 by the status ##########

fig6 = px.box(df, x='Status', y='Life expectancy ',title='Life Expectancy Distribution by Status (2000 to 2015)',animation_frame='Year',category_orders={'Year': sorted(df['Year'].unique())},labels={'Life expectancy': 'Life Expectancy', 'Status': 'Development Status'})

fig6.update_layout(
    xaxis_title='Development Status',
    yaxis_title='Life Expectancy',
    width=1200,
    height=1200
)

st.plotly_chart(fig6, use_container_width=True)

########## 7. Correlation map in order to study the columns that are influencing the life expectancy ##########

numeric_columns = df.select_dtypes(include=['float64']).columns # Filtering the non-numeric columns in order to do a correlation
correlation_matrix = df[numeric_columns].corr()

fig7 = px.imshow(
    correlation_matrix,
    color_continuous_scale='GnBu',
    labels=dict(x='Features', y='Features', color='Correlation'),
    title='Correlation Heatmap',
    width=1500,
    height=1000,
)

st.plotly_chart(fig7, use_container_width=True)

########## 8. Correlation between schooling and life expectancy by continent ##########

fig8 = px.scatter(df, x='Schooling', y='Life expectancy ', trendline="ols",title='Scatter Plot of Schooling vs Life Expectancy',labels={'Schooling': 'Years of Schooling', 'Life expectancy ': 'Life Expectancy'})

fig8.update_layout(
    xaxis_title='Years of Schooling',
    yaxis_title='Life Expectancy',
    width=1800,
    height=1000,
)

fig8.update_traces(
    line=dict(color='red', dash='solid'), 
    selector=dict(mode='lines')
)

st.plotly_chart(fig8, use_container_width=True)

########## 9. Correlation between income ressources and life expectancy by continent in 2014 ##########

df_2014 = df[df['Year'] == 2014]

fig9 = px.scatter(df_2014, x='Income composition of resources', y='Life expectancy ', color='Continent',hover_name='Country', title='Income Composition vs Life Expectancy',labels={'Income composition of resources': 'Income Composition of Resources', 'Life expectancy': 'Life Expectancy'})

fig9.update_layout(
    xaxis_title='Income Composition of Resources',
    yaxis_title='Life Expectancy',
    width=1800,
    height=1000,
)
fig9.update_traces(marker=dict(size=8))

st.plotly_chart(fig9, use_container_width=True)

########## 10. Average BMI by continent ##########

df_avg_bmi = df.groupby(['Continent', 'Year'])[' BMI '].mean().reset_index()

fig10 = px.bar(df_avg_bmi, x='Continent', y=' BMI ', color='Continent',animation_frame='Year',title='Average BMI Over the Years by Continent (2000-2014)',labels={' BMI ': 'Average BMI', 'Continent': 'Continent'},range_y=[df_avg_bmi[' BMI '].min(), df_avg_bmi[' BMI '].max()])
fig10.update_layout(
    xaxis_title='Continent',
    yaxis_title='Average BMI',
    width=1800,
    height=1000,
)

st.plotly_chart(fig10, use_container_width=True)

########## 11. Thinness between 1-19 years old accross countries ##########

fig11 = px.choropleth(
    df,
    locations='Country',
    locationmode='country names',
    color=' thinness  1-19 years',
    hover_name='Country',
    color_continuous_scale=px.colors.sequential.Plasma,
    title='Thinness between 1-19 years old accross countries',
    template='plotly',
    animation_frame='Year',
    category_orders={'Year': sorted(df['Year'].unique())}
)
fig11.update_geos(
    resolution=110,
    showcoastlines=True,
    coastlinecolor="Black",
    showland=True,
    landcolor="white",
)
fig11.update_layout(
    width=1500,  
    height=1000,  
)

st.plotly_chart(fig11, use_container_width=True)

########## 12. Violin plot on Alcohol Consumption by continent ##########

fig12 = px.violin(df, x='Continent', y='Alcohol', color='Continent',box=True,title='Violin plot on Alcohol Consumption by continent')
 
fig12.update_layout(
    xaxis_title='Continent',
    yaxis_title='Alcohol consumtion (in Liters)',
    legend_title='Continent',
    font=dict(size=12),
    width=1500,
    height=1200,
    margin=dict(l=20, r=20, t=60, b=20),
)

st.plotly_chart(fig12, use_container_width=True)

########## 13. Comparision on the evolution of HIV and Measles ##########

df_hiv_measles = df.groupby('Year')[[' HIV/AIDS', 'Measles ']].sum().reset_index()

fig13 = sp.make_subplots(rows=2, cols=1, subplot_titles=['HIV/AIDS', 'Measles'])

bar_trace_hiv = go.Bar(x=df_hiv_measles['Year'], y=df_hiv_measles[' HIV/AIDS'], name='HIV/AIDS')
bar_trace_measles = go.Bar(x=df_hiv_measles['Year'], y=df_hiv_measles['Measles '], name='Measles')

fig13.add_trace(bar_trace_hiv, row=2, col=1)
fig13.add_trace(bar_trace_measles, row=1, col=1)

fig13.update_layout(
    title='Number of Deaths by HIV and Measles (2000-2015)',
    xaxis_title='Year',
    yaxis_title='Number of Deaths',
    width=1800,
    height=1000,
)
fig13.update_xaxes(tickmode='linear')
fig13.update_xaxes( title_text='Year', row=2, col=1)

fig13.update_yaxes( title_text='Number of Deaths')

st.plotly_chart(fig13, use_container_width=True)

########## 14. Map on the evolution of Adult Mortality ##########

fig14 = px.choropleth(
    df,
    locations='Country',
    locationmode='country names',
    color='Adult Mortality',
    hover_name='Country',
    color_continuous_scale=px.colors.sequential.Plasma,
    title='Adult Mortality Across Countries',
    template='plotly',
    animation_frame='Year',
    category_orders={'Year': sorted(df['Year'].unique())}
)
fig14.update_geos(
    resolution=110,
    showcoastlines=True,
    coastlinecolor="Black",
    showland=True,
    landcolor="white",
)
fig14.update_layout(
    width=1500,  
    height=1000,  
)

st.plotly_chart(fig14, use_container_width=True)

########## 15. Map on the evolution of under five death to compare ##########

fig15 = px.choropleth(
    df,
    locations='Country',
    locationmode='country names',
    color='infant deaths',
    hover_name='Country',
    color_continuous_scale=px.colors.sequential.Plasma,
    title='Under five mortality Across Countries',
    template='plotly',
    animation_frame='Year',
    category_orders={'Year': sorted(df['Year'].unique())}
)
fig15.update_geos(
    resolution=110,
    showcoastlines=True,
    coastlinecolor="Black",
    showland=True,
    landcolor="white",
)
fig15.update_layout(
    width=1500,  
    height=1000,  
)

st.plotly_chart(fig15, use_container_width=True)