import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load the car data
@st.cache_data
def load_data():
    return pd.read_csv('data/cleaned_car_data_year.csv')

car_data = load_data()


# Data Summary
st.sidebar.title("Data Summary")
st.sidebar.text(f"Total Entries: {len(car_data)}")
st.sidebar.text(f"Unique Makes: {car_data['Make'].nunique()}")
st.sidebar.text(f"Average Price: {car_data['Price'].mean():.2f}")

# Sidebar filters
st.sidebar.title("Filters")
make_filter = st.sidebar.multiselect("Select Make", car_data['Make'].unique())
price_range = st.sidebar.slider("Price Range", float(0), float(car_data['Price'].max()), (float(0), float(car_data['Price'].max())))
kilometer_range = st.sidebar.slider("Kilometer Range", float(0), float(car_data['Kilometer'].max()), (float(0), float(car_data['Kilometer'].max())))

# Get the minimum and maximum years
min_year = min(car_data['Year'].unique())
max_year = max(car_data['Year'].unique())

# Generate a list of years from min to max
years = list(range(min_year, max_year + 1))

st.sidebar.title("Year")
year_cols = st.sidebar.columns(2)

# Set the default value of the "From" dropdown to the minimum year
start_year_filter = year_cols[0].selectbox("From", years, index=0)

# Set the default value of the "To" dropdown to the maximum year
end_year_filter = year_cols[1].selectbox("To", years, index=len(years)-1)

# Advanced Filters
transmission_filter = st.sidebar.multiselect("Select Transmission", car_data['Transmission'].unique())
fuel_type_filter = st.sidebar.multiselect("Select Fuel Type", car_data['Fuel Type'].unique())


# Apply filters
filtered_data = car_data[(car_data['Make'].isin(make_filter)) &
                         (car_data['Price'].between(price_range[0], price_range[1])) &
                         (car_data['Kilometer'].between(kilometer_range[0], kilometer_range[1])) &
                         (car_data['Year'] >= start_year_filter) &
                         (car_data['Year'] <= end_year_filter)]

# If Transmission and Fuel Type are not selected, include all vehicles
if transmission_filter:
    filtered_data = filtered_data[car_data['Transmission'].isin(transmission_filter)]
if fuel_type_filter:
    filtered_data = filtered_data[car_data['Fuel Type'].isin(fuel_type_filter)]
# Display filtered data
st.write(filtered_data)

# Histogram of Price
st.header("Histogram of Price")
fig_hist = px.histogram(filtered_data, x='Price', nbins=20)
st.plotly_chart(fig_hist)

# Scatter plot of Price vs. Kilometer
st.header("Scatter plot of Price vs. Kilometer")
fig_scatter = px.scatter(filtered_data, x='Kilometer', y='Price', color='Make', hover_data=['Model'])
st.plotly_chart(fig_scatter)


# Find the car with the maximum power for each make
max_power_cars = filtered_data.loc[filtered_data.groupby('Make')['Max Power'].idxmax()]
# Bar chart of Max Power by Make
st.header("Bar chart of Max Power by Make")
fig_max_power = px.bar(max_power_cars, x='Make', y='Max Power', color='Model', hover_data=['Model'])
st.plotly_chart(fig_max_power)

# Create a DataFrame that contains the count of each 'Make'
make_counts = filtered_data['Make'].value_counts().reset_index()
make_counts.columns = ['Make', 'Count']

# Create the bar chart
fig_make_count = px.bar(make_counts, x='Make', y='Count', color='Make')

# Display the figure in Streamlit
st.plotly_chart(fig_make_count)

# Pie chart of Fuel Type
st.header("Pie chart of Fuel Type")
fig_pie = px.pie(filtered_data, names='Fuel Type', title='Fuel Type Distribution')
st.plotly_chart(fig_pie)

# Box plot of Price by Transmission type
st.header("Box plot of Price by Transmission type")
fig_box = px.box(filtered_data, x='Transmission', y='Price')
st.plotly_chart(fig_box)


# Initialize an empty figure
fig = go.Figure()

# Iterate over the unique car makes
for make in filtered_data['Make'].unique():
    # Filter the data for the current make
    make_data = filtered_data[filtered_data['Make'] == make]

    # Calculate the mean price for each year for the current make
    mean_prices = make_data.groupby('Year')['Price'].mean().reset_index()

    # Create a scatter plot for the mean prices
    mean_price_trace = go.Scatter(
        x=mean_prices['Year'],
        y=mean_prices['Price'],
        mode='lines+markers',
        name=f'Mean Price of {make}'
    )

    # Add the scatter plot to the figure
    fig.add_trace(mean_price_trace)

# Set the y-axis to a log scale
fig.update_yaxes(type="log")

# Add title and labels
fig.update_layout(
    title="Price vs Age with Mean Price Trajectory for Each Make",
    xaxis_title="Age",
    yaxis_title="Price",
    hovermode="closest"
)

# Display the figure in Streamlit
st.plotly_chart(fig)