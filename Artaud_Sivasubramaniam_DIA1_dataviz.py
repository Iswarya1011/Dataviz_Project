import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp
from geopy.geocoders import Nominatim



########## Title ##########

# Reducing margins
st.markdown(
    """
    <style>
        .block-container {
            max-width: 1500px;
            margin-left: auto;
            margin-right: auto;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title('Dataviz project')
st.header('ARTAUD Lucas & SIVASUBRAMANIAM Iswarya DIA 1', divider=False)

########## Context and motivation ##########

st.header('Context and motivation', divider='blue')
st.write('The data set chosen is a statistical data on factors influencing Life Expectancy. The data comes from the World Helath Organization for a period of time of 15 years.')
st.write('Many studies in the past have explored the factors influencing life expectancy, centering around demographic variables, income composition, and mortality rates. However, these studies often neglected the impact of immunization and the Human Development Index. Additionally, some prior research relied on a one-year dataset for all countries but doing this research r a period of time of 15 year enables us to visualise the changes over time. This data set allows us to do a country based observation to identify the main factors that are contributing to lower life expectancy.')
st.write('This data-set counts health factors of 193 countries over 15 years (2000-2015). We have 22 columns and 2938 rows.')
st.write('From our preliminary analysis, population, Hepatitis B and GDP columns contains most of the missing data.We decided not to remove all the missing values because we will delete the entire row and we will lose informations.')
st.write('The motivation of our project is to analyze the different factors that influences the life expectancy and compare on different scales (between continents, developed / developing etc...).')
st.write('We hope to learn more about the various factors affecting life expectancy and how those findings can guide public health interventions and policies. Targeted healthcare initiatives could be guided, for instance, by identifying particular regions or demographic groups experiencing challenges with life expectancy. Furthermore, knowledge of how social determinants, economic variables, and immunizations affect life expectancy can support evidence-based decision-making at the national and international levels. )')

########## Creation of new columns ##########

df = pd.read_csv("Life Expectancy Data.csv")
unique_countries = pd.read_csv("countries.csv")

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

df = pd.merge(df, unique_countries, on='Country', how='left')

########## 1. Average life expectancy and population over the years ##########

st.header('1. Average life expectancy and population over the years', divider='blue')

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
    title_text="Average Life Expectancy and Population Over Time",
    font=dict(size=12),
    width=1500,
    height=700,
    margin=dict(l=20, r=20, t=60, b=20),
)

st.plotly_chart(fig1, use_container_width=True)
st.write("Between 2000 and 2015 we can see that the average life expectancy has increased from 67 to 72 years. For the average population, it is inconsistent over time, in fact we can see ups and downs,especially during 2008 and 2010")

########## 2. Life Expectancy over the years of the top 10 and bottom 10 countries ##########

st.header('2. Life Expectancy over the years of the top 10 and bottom 10 countries', divider='blue')

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
st.write('The top 5 countries having the best average on life expectanvcy over the years are France, Sweeden, Iceland, Japan and Switzerland. The bottom 5 countries having the worrt average on life expectancy over the years are Sierra Leone, Malawi, Angola, Central African Republic and Lesotho.We can notice that the top 5 countries have an increasing on life expectancy (from 81-88) but it stabilises from 2009, whereas for the bottom 5 we can see a considerable growth (from 39 to 51 for certain countries). We can also notice that the top 5 countries belong to the northern hemisphere unlike the bottom 5 that are African Countries.')

########## 3. Violin Plot for Life Expectancy by Continent ##########

st.header('3. Violin Plot for Life Expectancy by Continent', divider='blue')

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
st.write('We can conclude that Africa is the continent where life expectancy is low, so the authorities should concentrate on this continent. The second continent having a low average is Asia.')

########## 4. Pie chart for the distribution of countries by Status ##########

st.header('4. Pie chart for the distribution of countries by Status', divider='blue')

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
st.write('This dataset contains 17.4% of develoved countries and 82.6% of developping countries. This is a good ratio because usually it is developpping countries that have less life expectancy.')

########## 5. Comparing the GDP from 2000 to 2015 by the status ##########

st.header('5. Comparing the GDP from 2000 to 2015 by the status', divider='blue')

df_gdp_avg=df.groupby(['Year', 'Status'])['GDP'].mean().reset_index()

fig5 = px.bar(df_gdp_avg, x='Status', y='GDP', color='Status', title='Average GDP by Country Status Over Years',animation_frame='Year', barmode='group')
fig5.update_layout(xaxis_title='Year', yaxis_title='Average GDP (USD)', width=1200, height=800)

st.plotly_chart(fig5, use_container_width=True)
st.write('Over the years there is a big gap between the GDP of developed countries and developing countries taking into account the fact that  we have only 17% of developped countries.The gap between GDP and status is considerable. In 2000 we have a gap of 12 842 USD to 20 057 in 2014. There is an increase of GDP on both sides, but the increase is greater for developed countries.')

########## 6. Comparing the life expectancy from 2000 to 2015 by the status ##########

st.header('6. Comparing the life expectancy from 2000 to 2015 by the status', divider='blue')

fig6 = px.box(df, x='Status', y='Life expectancy ',title='Life Expectancy Distribution by Status (2000 to 2015)',animation_frame='Year',category_orders={'Year': sorted(df['Year'].unique())},labels={'Life expectancy': 'Life Expectancy', 'Status': 'Development Status'})

fig6.update_layout(
    xaxis_title='Development Status',
    yaxis_title='Life Expectancy',
    width=1500,
    height=1000
)

st.plotly_chart(fig6, use_container_width=True)
st.write('We can notice that there is an evolution of the life expactancy on both sides but for developing countries the values are more scattered than for developed countries where it is concentrated.')

########## 7. Correlation map in order to study the columns that are influencing the life expectancy ##########

st.header('7. Correlation map in order to study the columns that are influencing the life expectancy', divider='blue')

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
st.write("From this correlation matrix we can see that Schooling, Income composition of ressources and BMI are highly corelated to life expectancy. It means that it influences the growth of life expectancy. Let's concentrate on the analysis of these columns.")

########## 8. Correlation between schooling and life expectancy by continent ##########

st.header('8. Correlation between schooling and life expectancy by continent', divider='blue')

fig8 = px.scatter(df, x='Schooling', y='Life expectancy ', trendline="ols",title='Scatter Plot of Schooling vs Life Expectancy',labels={'Schooling': 'Years of Schooling', 'Life expectancy ': 'Life Expectancy'})

fig8.update_layout(
    xaxis_title='Years of Schooling',
    yaxis_title='Life Expectancy',
    width=1500,
    height=1000,
)

fig8.update_traces(
    line=dict(color='red', dash='solid'), 
    selector=dict(mode='lines')
)

st.plotly_chart(fig8, use_container_width=True)
st.write('We can see that we have a cleary correlation line between schooling and Life expectancy. The more the years of schooling is the better is life expectancy.')

########## 9. Correlation between income ressources and life expectancy by continent in 2014 ##########

st.header('9. Correlation between income ressources and life expectancy by continent in 2014', divider='blue')

df_2014 = df[df['Year'] == 2014]

fig9 = px.scatter(df_2014, x='Income composition of resources', y='Life expectancy ', color='Continent',hover_name='Country', title='Income Composition vs Life Expectancy',labels={'Income composition of resources': 'Income Composition of Resources', 'Life expectancy': 'Life Expectancy'})

fig9.update_layout(
    xaxis_title='Income Composition of Resources',
    yaxis_title='Life Expectancy',
    width=1500,
    height=1000,
)
fig9.update_traces(marker=dict(size=8))

st.plotly_chart(fig9, use_container_width=True)
st.write('Here we are only concentrating in 2014 because 2015 has many missing values, moreover it enables to clealy see the correlation. We can note that most contries from Africa have an Income composition resouces of 0.34-0.59 and a life expectancy of 48-68. For European countries we have a higher income composition of ressources and a better life expectancy.This explains the correlation between both the criterias, the more the income composition of ressources is the better is the life expectancy.')

########## 10. Average BMI by continent ##########

st.header('10. Average BMI by continent', divider='blue')

df_avg_bmi = df.groupby(['Continent', 'Year'])[' BMI '].mean().reset_index()

fig10 = px.bar(df_avg_bmi, x='Continent', y=' BMI ', color='Continent',animation_frame='Year',title='Average BMI Over the Years by Continent (2000-2014)',labels={' BMI ': 'Average BMI', 'Continent': 'Continent'},range_y=[df_avg_bmi[' BMI '].min(), df_avg_bmi[' BMI '].max()])
fig10.update_layout(
    xaxis_title='Continent',
    yaxis_title='Average BMI',
    width=1500,
    height=1000,
)

st.plotly_chart(fig10, use_container_width=True)
st.write('The body mass index (BMI) is a measure that uses your height and weight to work out if your weight is healthy.Compared to the other countinents Africa has the least average BMI score.This can explain the fact that it has a less life expectancy.Indeed a less BMI means that they are unhealthy. This can be caused by malnutrition and provoke earlier death.')

########## 11. Thinness between 1-19 years old accross countries ##########

st.header('11. Thinness between 1-19 years old accross countries', divider='blue')

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
st.write('In order to analyse our hypothesis made on the last visual we have made this map representing thinness between 1-19 years old accross countries.We can see that South Asian countries (like India, Pakistan) have the highest number of thinness between 1-19 year old. Compared to others, African countries are also having a relatively high number of thinness between 1-19 year old but we can also see that this has improved a little over the years. This can be an explaination for the BMI value.')

########## 12. Violin plot on Alcohol Consumption by continent ##########

st.header('12. Violin plot on Alcohol Consumption by continent', divider='blue')

fig12 = px.violin(df, x='Continent', y='Alcohol', color='Continent',box=True,title='Violin plot on Alcohol Consumption by continent')
 
fig12.update_layout(
    xaxis_title='Continent',
    yaxis_title='Alcohol consumtion (in Liters)',
    legend_title='Continent',
    font=dict(size=12),
    width=1500,
    height=1000,
    margin=dict(l=20, r=20, t=60, b=20),
)

st.plotly_chart(fig12, use_container_width=True)
st.write('Europe is the continent where the alcohol consumtion is high compared to other continents. We can also see that it is highly spreaded.')

########## 13. Comparision on the evolution of HIV and Measles ##########

st.header('13. Comparision on the evolution of HIV and Measles', divider='blue')

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
    width=1500,
    height=1000,
)
fig13.update_xaxes(tickmode='linear')
fig13.update_xaxes( title_text='Year', row=2, col=1)

fig13.update_yaxes( title_text='Number of Deaths')

st.plotly_chart(fig13, use_container_width=True)
st.write('Health wise, world wide we can see there is significant fall in the number of HIV and Measles. This decrease can explain the increase of life expectancy world wide.')

########## 14. Map on the evolution of Adult Mortality ##########

st.header('14. Map on the evolution of Adult Mortality', divider='blue')

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
st.write("Over the years African countries and Asian countries have the highest number of adult deaths. This can be explained by health developpement, malnutitoin and also geo politic situation (we don't have more informations about this third point).")

########## 15. Map on the evolution of under five death to compare ##########

st.header('15. Map on the evolution of under five death to compare', divider='blue')

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
st.write('Over the years India and China, which are the most populated countries in the world, have a high number of under 5 year old death. We have already seen that India was also the country having the highest numbre of thinness between 1-19. These two elements can be correlated.')
