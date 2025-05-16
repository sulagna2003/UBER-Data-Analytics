import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="UBER!!!",page_icon=":car:",layout="wide")

st.title(" :car: UBER DASHBOARD")
st.markdown(
    """
    <style>
    body {
        background-color: #800080; /* Purple background color */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Allow the user to upload a CSV file
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Read the uploaded CSV file
    df = pd.read_csv(uploaded_file, encoding="ISO-8859-1")
    st.write(df)
else:
    st.warning("Please upload a CSV file.")
    
# Assuming df is your DataFrame
# Parse START_DATE* column to datetime
# Adjust the format string according to the actual format of your dates
df["START_DATE*"] = pd.to_datetime(df["START_DATE*"], format='%d-%m-%Y %H:%M', errors='coerce')

# Drop rows with NaT values if any date strings couldn't be parsed
df = df.dropna(subset=["START_DATE*"])

# Getting the min and max date
startDate = df["START_DATE*"].min()
endDate = df["START_DATE*"].max()

# Create Streamlit columns
col1, col2 = st.columns(2)

with col1:
    date1 = st.date_input("Start Date", startDate)

with col2:
    date2 = st.date_input("End Date", endDate)

# Convert the selected dates to datetime
date1 = pd.to_datetime(date1)
date2 = pd.to_datetime(date2)

# Filter the DataFrame based on the selected date range
df_filtered = df[(df["START_DATE*"] >= date1) & (df["START_DATE*"] <= date2)].copy()

st.sidebar.header("Choose your filter:")

#create for purpose
purpose=st.sidebar.multiselect("Choose Purpose",df["PURPOSE*"].unique())
if not purpose:
    df2=df.copy()
else:
    df2=df[df["PURPOSE*"].isin(purpose)]

#create for start
start=st.sidebar.multiselect("Start location",df["START*"].unique())
if not start:
    df2=df.copy()
else:
    df2=df[df["START*"].isin(start)]

#create for stop
stop=st.sidebar.multiselect("Stop location",df["STOP*"].unique())
if not start:
    df2=df.copy()
else:
    df2=df[df["STOP*"].isin(stop)]
#Filter the data based on purpose,start and stop location
if not purpose and not start and not stop:
    filtered_df = df
elif not start and not stop:
    filtered_df = df[df["PURPOSE*"].isin(purpose)]
elif not purpose and not stop:
    filtered_df = df[df["START*"].isin(start)]
elif start and stop:
    filtered_df = df[df["START*"].isin(start) & df["STOP*"].isin(stop)]
elif purpose and stop:
    filtered_df = df[df["PURPOSE*"].isin(purpose) & df["STOP*"].isin(stop)]
elif purpose and start:
    filtered_df = df[df["PURPOSE*"].isin(purpose) & df["START*"].isin(start)]
elif stop:
    filtered_df = df[df["STOP*"].isin(stop)]
else:
    filtered_df = df[df["PURPOSE*"].isin(purpose) & df["START*"].isin(start) & df["STOP*"].isin(stop)]

category_df= filtered_df.groupby(by=["CATEGORY*"],as_index=False)["MILES*"].sum()
category_df1= filtered_df.groupby(by=["PURPOSE*"],as_index=False)["MILES*"].sum()

with col1:
    st.subheader("CATEGORY WISE TRIPS")
    fig = px.pie(filtered_df, values = "MILES*", names = "CATEGORY*", hole = 0.5)
    fig.update_traces(text = filtered_df["MILES*"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

with col2:
    fig = px.bar(category_df, x = "CATEGORY*", y = "MILES*",
                 template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height = 200)

with col1:
    st.subheader("PURPOSE WISE TRIPS")
    fig = px.pie(filtered_df, values = "MILES*", names = "PURPOSE*", hole = 0.4)
    fig.update_traces(text = filtered_df["MILES*"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

with col2:
    fig = px.bar(category_df1, x = "PURPOSE*", y = "MILES*",
                 template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height = 200)

cl1,cl2 = st.columns(2)

with cl1:
    with st.expander("CATEGORY WISE TRIPS DATA"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv=category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data",data=csv,file_name="Category.csv",mime="test/csv",
                           help='Click here to download the data as a csv file')
with cl2:
    with st.expander("PURPOSE WISE TRIPS DATA "):
        purpose=filtered_df.groupby(by=["PURPOSE*"],as_index=False)["MILES*"].sum()
        st.write(category_df1.style.background_gradient(cmap="Oranges"))
        csv=category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data",data=csv,file_name="Purpose.csv",mime="test/csv",
                           help='Click here to download the data as a csv file')
filtered_df["month_year"]=filtered_df["START_DATE*"].dt.to_period("M")
st.subheader('Time Series Analysis')
linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["MILES*"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y="MILES*", labels = {"Sales": "Amount"},height=500, width = 1000,template="gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("CLICK TO VIEW TIMESERIES DATA"):
    st.write(linechart.T.style.background_gradient(cmap="Oranges"))
    csv=linechart.to_csv(index=False).encode('utf-8')
    st.download_button("Download Data",data=csv,file_name="TimeSeries.csv",mime="test/csv",
                           help='Click here to download the data as a csv file')


st.markdown("MONTH WISE MILES TABLE BASED ON CATEGORY")
filtered_df["month"] = filtered_df["START_DATE*"].dt.month_name()
sub_category_Year = pd.pivot_table(data = filtered_df, values = "MILES*", index = ["CATEGORY*"],columns = "month")
st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

st.markdown("MONTH WISE MILES TABLE BASED ON PURPOSE")
filtered_df["month"] = filtered_df["START_DATE*"].dt.month_name()
sub_category_Year = pd.pivot_table(data = filtered_df, values = "MILES*", index = ["PURPOSE*"],columns = "month")
st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

with st.expander("Click to download original dataset"):
    csv = df.to_csv(index = False).encode('utf-8')
    st.download_button('Download Data', data = csv, file_name = "Uber Drives fedit.csv",mime = "text/csv")

