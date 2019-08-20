#!/usr/bin/env python
# coding: utf-8

# In[1]:



from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

# In[2]:


import numpy as np
import pandas as pd


# In[6]:


import datetime as dt


# # Reflect Tables into SQLAlchemy ORM

# In[7]:


# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


# In[8]:


engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# In[9]:


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)


# In[10]:


# We can view all of the classes that automap found
Base.classes.keys()


# In[11]:


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


# In[12]:


# Create our session (link) from Python to the DB
session = Session(engine)


# # Exploratory Climate Analysis

# In[13]:


# Design a query to retrieve the last 12 months of precipitation data and plot the results

# Calculate the date 1 year ago from the last data point in the database

# Perform a query to retrieve the data and precipitation scores

# Save the query results as a Pandas DataFrame and set the index to the date column

# Sort the dataframe by date

# Use Pandas Plotting with Matplotlib to plot the data


# In[14]:


import datetime as dt


# In[15]:


# Calculate the date 1 year ago from the last data point in the database
year_ago = dt.date(2017, 8, 23)- dt.timedelta(days=365)
print(year_ago)


# In[16]:


# Design a query to retrieve the last 12 months of precipitation data and plot the results
prcp_data = session.query(Measurement.prcp, Measurement.date).filter(Measurement.date >= '2016-08-23').order_by(Measurement.date).all()
print(prcp_data)


# In[17]:


# Save the query results as a Pandas DataFrame and set the index to the date column
# Sort the dataframe by date
precip_data = pd.DataFrame(prcp_data, columns = ['precipitation', 'date'])
precip_data.set_index('date', inplace=True)
#precip_data['precipitation'].fillna(0, inplace=True)
precip_data.head(10)


# In[18]:


# Use Pandas Plotting with Matplotlib to plot the data
precip_data.plot(y="precipitation", figsize=(10,5))
plt.title("Precipitation of Last 12 Months")
plt.ylabel("Precipitation")
plt.xlabel("Date")
plt.show()
plt.tight_layout()


# ![precipitation](Images/precipitation.png)

# In[19]:


# Use Pandas to calcualte the summary statistics for the precipitation data
precip_data['precipitation'].describe()


# ![describe](Images/describe.png)

# In[20]:


from pprint import pprint


# In[21]:


# Design a query to show how many stations are available in this dataset?
no_of_stations = session.query(func.count(Station.station)).all()
pprint(no_of_stations)


# In[22]:


from pprint import pprint


# In[23]:


# What are the most active stations? (i.e. what stations have the most rows)?
# List the stations and the counts in descending order.
most_active = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
pprint(most_active)


# In[24]:


# Using the station id from the previous query, calculate the lowest temperature recorded, 
# highest temperature recorded, and average temperature most active station?
most_active_station = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.station == 'USC00519281').all()
print(most_active_station)


# In[25]:


# Choose the station with the highest number of temperature observations.
# Query the last 12 months of temperature observation data for this station and plot the results as a histogram
most_active_temps = session.query(Measurement.station, Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').all()
#print(most_active_temps)
year_ago_active_temps= dt.date(2017, 8, 18)- dt.timedelta(days=365)
#print(year_ago_active_temps)
org_hist_data = session.query(Measurement.tobs, func.count(Measurement.tobs)).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= '2016-08-18').group_by(Measurement.tobs).all()
#pprint(hist_data)
hist_data =session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= '2016-08-18').all()
pprint(hist_data)


# In[26]:


#Make a pandas DataFrame to hold the histogram data
active_temp_hist = pd.DataFrame(org_hist_data, columns = ['temperature', 'temp frequency'])
histogram_temps = pd.DataFrame(hist_data, columns = ['temperature'])
histogram_temps.head()


# In[27]:


#Create histogram from USC00519281 going back a year from its last temperature reading
x = []
x.append(histogram_temps['temperature'])
plt.hist(x,  bins=12, label='tobs')
plt.ylabel('Frequency');
plt.legend()
plt.show()


# In[28]:


from flask import Flask, jsonify


# In[29]:


prcp_data2 = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= '2016-08-23').all()
print(prcp_data2)


# In[30]:


#Query for temperature and dates a year ago from the last data set
temperature_last_year = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= '2016-08-23').all()
#Query for dates
dates4 = session.query(Measurement.date).all()
dates4


# In[31]:


#Convert queries into dictionaries for climate app
prcp_data3 = dict(prcp_data2)
most_active2 = dict(most_active)
temp_last_year2 = dict(temperature_last_year)


# In[32]:


session.close()


# In[33]:


from flask import Flask


# In[42]:


#Flask Setup
app = Flask(__name__)
#Flask Routes

@app.route("/")
def welcome():
    return (
        f"Welcome to the Valmont Climate App<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    return jsonify(prcp_data3)
   
        
@app.route("/api/v1.0/stations")
def stations():
    return jsonify(most_active2)

    
@app.route("/api/v1.0/tobs")
def temps():
    return jsonify(temp_last_year2)


@app.route("/api/v1.0/<strt_date>")
def tempsperdate(strt_date):
    session = Session(engine)
    query1 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).    filter(Measurement.date >= strt_date).all()
    dt_range = []
    for dates in query1:
        range_dt_dict = {}
        range_dt_dict["Min Temp"]=query1[0][0]
        range_dt_dict["Avg Temp"]=query1[0][1]
        range_dt_dict["Max Temp"]=query1[0][2]
        dt_range.append(range_dt_dict)
    
    session.close()
    
    return jsonify(dt_range)


        
        
@app.route("/api/v1.0/<start_date>/<end_date>")
def tempsperdate2(start_date, end_date):
    session = Session(engine)
    query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).    filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    date_range = []
    for data in query:
        range_date_dict = {}
        range_date_dict["Min Temp"]=query[0][0]
        range_date_dict["Avg Temp"]=query[0][1]
        range_date_dict["Max Temp"]=query[0][2]
        date_range.append(range_date_dict)
    
    session.close()
    
    return jsonify(date_range)
    
    
        
        
if __name__ == "__main__":
     app.run()


# In[35]:


# Use your previous function `calc_temps` to calculate the tmin, tavg, and tmax 
# for your trip using the previous year's data for those same dates.
def calc_temps(start_date, end_date):
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

print(calc_temps('2012-06-23', '2012-06-29'))


# In[36]:


# Plot the results from your previous query as a bar chart. 
# Use "Trip Avg Temp" as your Title
# Use the average temperature for the y value
# Use the peak-to-peak (tmax-tmin) value as the y error bar (yerr)
plt.figure(figsize = (3, 6), dpi= 70)
mean = (73.09)
position = [0]
peak_to_peak = (13)
plt.bar(position, mean, yerr=peak_to_peak)
plt.title("Trip Avg Temp")
plt.ylabel("Temp (F)")


# In[37]:


#Calculated the total amount of rainfall for a year per weather station - Question was confusing as asked.
# Calculate the total amount of rainfall per weather station for your trip dates using the previous year's matching dates.
# Sort this in descending order by precipitation amount and list the station, name, latitude, longitude, and elevation
new = session.query(Measurement.station, Station.name, func.count(Measurement.prcp), Station.latitude, Station.longitude, Station.elevation).filter(Measurement.station == Station.station).filter(Measurement.date >= '2012-06-29').filter(Measurement.date <= '2013-06-29').group_by(Station.name).order_by(func.count(Measurement.prcp).desc()).all()

print(new)
     


# ## Optional Challenge Assignment

# In[66]:


# Create a query that will calculate the daily normals 
# (i.e. the averages for tmin, tmax, and tavg for all historic data matching a specific month and day)

def daily_normals(date):
   
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    return session.query(*sel).filter(func.strftime("%m-%d", Measurement.date) == date).all()
    
daily_normals("09-09")


# In[67]:


# calculate the daily normals for your trip
# push each tuple of calculations into a list called `normals`
# Set the start and end date of the trip
# Use the start and end date to create a range of dates
# Stip off the year and save a list of %m-%d strings
# Loop through the list of %m-%d strings and calculate the normals for each date

    


# In[52]:


# Load the previous query results into a Pandas DataFrame and add the `trip_dates` range as the `date` index


# In[41]:


# Plot the daily normals as an area plot with `stacked=False`

