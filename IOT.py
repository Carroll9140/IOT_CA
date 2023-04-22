import boto3
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import plotly.express as px
import streamlit as st

#Pulling data from AWS
REGION_NAME = 'eu-west-1'
TABLE_NAME = 'IOT_CA1_DataTable'
dynamodb = boto3.resource('dynamodb', region_name=REGION_NAME)
table = dynamodb.Table(TABLE_NAME)
response = table.scan()
data = response['Items']

while 'LastEvaluatedKey' in response:
    response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
    data.extend(response['Items'])

#Formatting time in dataframe
table = pd.DataFrame(data)
table['sample_time'] = table['sample_time'].apply(lambda x: datetime.utcfromtimestamp(float(x / 1000)).strftime('%Y-%m-%d %H:%M:%S'))
table['sample_time'] = pd.to_datetime(table['sample_time'])

#Creating Dataframe of previous hours sensor data
hour_table = table[table['sample_time']>=(datetime.now() - timedelta(hours=2))]['device_data']
hour_table = pd.DataFrame.from_dict(hour_table)
hour_split = hour_table['device_data'].apply(pd.Series)
hour_table = pd.concat([hour_table.drop(columns=['device_data']),hour_split],axis=1)

#Creating Dataframe of all sensor data
table = pd.DataFrame.from_dict(table)
split = table['device_data'].apply(pd.Series)
table = pd.concat([table.drop(columns=['device_data']),split],axis=1)

#Creating Dashboard

st.title ("IOT Dashboard")
st.header("Node-Red Data")

#Table of all data collected
st.markdown("Sensors Latest Values")
st.dataframe(table.sort_values('sample_time', ascending = False))

#Dividing dasboard into multiple columns
kpi1, kpi2, kpi3 = st.columns(3)
kpi4, kpi5, kpi6 = st.columns(3)
kpi7, kpi8, kpi9 = st.columns(3)
kpi10, kpi11, kpi12 = st.columns(3)

#Descriptive Stats for each metric value in last hour
kpi1.metric(label = 'Max Temperature', 
            value = int(np.max(hour_table['temperature'])))

kpi2.metric(label = 'Max Humidity', 
            value = int(np.max(hour_table['humidity'])))

kpi3.metric(label = 'Max Pressure', 
            value = int(np.max(hour_table['pressure'])))

kpi4.metric(label = 'Min Temperature', 
            value = int(np.min(hour_table['temperature'])))

kpi5.metric(label = 'Min Humidity', 
            value = int(np.min(hour_table['humidity'])))

kpi6.metric(label = 'Min Pressure', 
            value = int(np.min(hour_table['pressure'])))

kpi7.metric(label = 'Mean Temperature', 
            value = int(np.mean(hour_table['temperature'])))

kpi8.metric(label = 'Mean Humidity', 
            value = int(np.mean(hour_table['humidity'])))

kpi9.metric(label = 'Mean Pressure', 
            value = int(np.mean(hour_table['pressure'])))

kpi10.metric(label = 'Median Temperature', 
            value = int(np.median(hour_table['temperature'])))

kpi11.metric(label = 'Median Humidity', 
            value = int(np.median(hour_table['humidity'])))

kpi12.metric(label = 'Median Pressure', 
            value = int(np.median(hour_table['pressure'])))

fig_col1, fig_col2, fig_col3 = st.columns(3)

#Bar Charts for each metric
with fig_col1:
     st.markdown("Temperature Bar Chart")
     fig1 = px.bar(data_frame=table, y = table['temperature'], x = table['sample_time'])
     st.write(fig1)

with fig_col2:
     st.markdown("Humidity Bar Chart")
     fig2 = px.bar(data_frame=table, y = table['humidity'], x = table['sample_time'])
     st.write(fig2)

with fig_col3:
     st.markdown("Pressure Bar Chart")
     fig3 = px.bar(data_frame=table, y = table['pressure'], x = table['sample_time'])
     st.write(fig3)