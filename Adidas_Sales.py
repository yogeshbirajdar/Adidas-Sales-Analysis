import streamlit as st
import pandas as pd
import datetime
from PIL import Image  # PIL -->For Processing Image
import plotly.express as px  # plotly --> For Interactive Data Visualization
import plotly.graph_objects as go

# Reading the Data from excel file

df = pd.read_excel("Adidas.xlsx")

st.set_page_config(page_title="Adidas", layout="wide")

st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)
image = Image.open("adidas-logo.jpg")

col1, col2, col3 = st.columns([0.20, 0.60, 0.20])
kpi1, kpi2, kpi3 = st.columns(3)

# KPI styling

st.markdown("""
<style>
/* Fix overall page width */
.block-container {
    padding-top: 1rem;
    max-width: 95%;
}

/* KPI Box Styling */
.css-1wivap2, [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
    font-size: 22px !important;
    font-weight: 700 !important;
}

[data-testid="stMetric"] {
    background: rgb(45, 120, 189);
    color: white !important;
    border-radius: 15px;
    padding: 20px !important;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.12);
}
</style>
""", unsafe_allow_html=True)

st.write("""
<style>
.st-emotion-cache-467cry p {
    word-break: break-word;
    margin-top: 15px;
    margin-left: 0px;
    margin-right: 0px;
}
</style>
""", unsafe_allow_html=True)



with col1:
    st.image(image, width=100)

html_title = """
    <style>
    .title-test {
    font-size:20 px;
    font-weight:bold;
    padding:5px
    border-radius:6px
    }
    </style><h1 class="title-test">Adidas Sales Dashboard</h1></center>"""

with col2:
    st.markdown(html_title, unsafe_allow_html=True)


with col3:
    box_date = str(datetime.datetime.now().strftime("%d %B %Y"))
    st.write(f"Last update by: \n {box_date}")

# Create Region Filter

region = st.sidebar.multiselect("Pick The Region", df["Region"].unique())

if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]


# Create State Filter

state = st.sidebar.multiselect("Pick The State", df2["State"].unique())

if not state:
    df3 = df2.copy()
else:
    df3 = df[df["State"].isin(state)]


# Create for City

city = st.sidebar.multiselect("Pick the City", df3["City"].unique())

if not city:
    df4 = df3.copy()
else:
    df4 = df3[df3["City"].isin(city)]

#Filter the data based on choosen like (Region, State, City)

if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df = df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filtered_df = df3[df["City"].isin(city)]
else:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isni(state) & df3["City"].isin(city)]


# KPI creation

def format_number(num):
    if num >= 1_000_000:
        return f"${num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"${num/1_000:.2f}K"
    else:
        return f"${num:.0f}"

total_sales = filtered_df["TotalSales"].sum()
total_quantity = filtered_df["UnitsSold"].sum()
total_profit = filtered_df["OperatingProfit"].sum()

with kpi1:
    kpi1.metric("Total Sales", format_number(total_sales))
    

with kpi2:
    kpi2.metric("Total_Quantity", format_number(total_quantity))

with kpi3:
    kpi3.metric("Total_Profit", format_number(total_profit))


col4, col5 = st.columns((2))


retailer_df = filtered_df.groupby(by = ["Retailer"], as_index = False)["TotalSales"].sum()

retailer_df["RetailerSales"] = retailer_df["TotalSales"].apply(format_number)


with  col4:
    st.subheader("Retailer wise Sales")
    fig = px.bar(retailer_df,
                 x = "Retailer",
                 y = "TotalSales",
                 labels={"Retailer":"Retailer Name"},
                 text = retailer_df["RetailerSales"],
                 hover_data= "TotalSales",
                 template="gridon", height=500)
    st.plotly_chart(fig, use_container_width=True)


view1, dwn1, view2, dwn2 = st.columns([0.20, 0.20, 0.20, 0.20])

with view1:
    expander = st.expander("Retailer Wise Sales")
    data = filtered_df[["Retailer", "TotalSales"]].groupby(by="Retailer")["TotalSales"].sum()
    expander.write(data)

with dwn1:
    st.download_button("Get Data", data.to_csv().encode("utf-8"),
                       file_name="Retailer_Sales.csv", mime="text/csv")
    

filtered_df["Month_Year"] = filtered_df["InvoiceDate"].dt.strftime("%b'%y")
result = filtered_df.groupby(by= filtered_df["Month_Year"])["TotalSales"].sum().reset_index()

with col5:
    st.subheader("Total Sales over Time")
    fig1 = px.line(
        result,
        x= "Month_Year",
        y = "TotalSales",
        markers= True,
        template="gridon")
    fig1.update_traces(text=result["TotalSales"], textposition="top center")
    st.plotly_chart(fig1, use_container_width=True)

with view2:
    expander = st.expander("Monthly Sales")
    data = result
    expander.write(data)

with dwn2:
    st.download_button("Get Data", data = result.to_csv().encode("utf-8"),
                       file_name="Monthly_Sales.csv", mime="text/csv")
    

st.divider() # IT create a line wchich devide 

col_1, col_2, col_3 = st.columns([0.5, 0.25, 0.25])

# Horizontal Bar chart

products_sales = filtered_df.groupby(by = "Product", as_index= False)["TotalSales"].sum()

products_sales["TotalSalesFormated"] = products_sales["TotalSales"].apply(format_number)

with col_1:
    st.subheader("Product wise Sales")
    fig_1 = px.bar(products_sales,
               x = "TotalSales",
               y = "Product",
               orientation="h",
               labels ={"TotalSales":"Total Sales {$}", "Product":"Product Name"},
               text = products_sales["TotalSalesFormated"],
               hover_data=["TotalSalesFormated"],
               template= "gridon")
    st.plotly_chart(fig_1, use_container_width=True)

# PIE chart with explode

pie_df = filtered_df.groupby("SalesMethod")["TotalSales"].sum().reset_index()

sorted_positions = pie_df["TotalSales"].argsort()[::-1]

pull_values = [0] * len(pie_df)

pull_scale = [0.12, 0.09, 0.09]

for i, pos in enumerate(sorted_positions):
    if i < len(pull_scale):
        pull_values[pos] = pull_scale[i]   # assign pull based on rank
    else:
        break

with col_2:
    st.subheader("Sales-Method Wise Sales")
    fig_2 = px.pie(pie_df, values="TotalSales", names="SalesMethod", template="gridon")
    fig_2.update_traces(text = pie_df["SalesMethod"], textposition = "outside", pull=pull_values, showlegend=False)
    st.plotly_chart(fig_2)

#Donut chart

donut_df = filtered_df.groupby(by = "SalesMethod")["OperatingMargin"].mean().reset_index()

with col_3:
    st.subheader("Profitability by Sales-Method")
    fig_3 = px.pie(donut_df, values="OperatingMargin", names="SalesMethod", template="gridon")
    fig_3.update_traces(text= donut_df["SalesMethod"], hole=0.5, textposition = "outside", pull=[0.02, 0.02, 0.02], showlegend = False)
    st.plotly_chart(fig_3)

view_1, dwn_1, view_2, dwn_2, view_3, dwn_3 = st.columns([0.20, 0.05, 0.10, 0.05, 0.10, 0.05])

with view_1:
    expander = st.expander("Product wise Sales")
    data = products_sales
    expander.write(data)

with dwn_1:
    st.download_button("Get Data", data = products_sales.to_csv().encode("utf-8"),
                       file_name= "Product_wise_Sales.csv", mime="text/csv")

with view_2:
    expander = st.expander("Sales-Method Wise Sales")
    data = pie_df
    expander.write(data)

with dwn_2:
    st.download_button("Get Data", data = pie_df.to_csv().encode("utf-8"),
                       file_name="MoSales-Method_Wise_Saless.csv", mime="text/csv")
    
with view_3:
    expander = st.expander("Profitibility by Sales-Method")
    data = donut_df
    expander.write(data)

with dwn_3:
    st.download_button("Get Data", data = donut_df.to_csv().encode("utf-8"),
                       file_name="Profitibility_by_Sales-Method.csv", mime="text/csv")

st.divider()

result1 = filtered_df.groupby(by="State")[["TotalSales", "UnitsSold"]].sum().reset_index()

# add the units sold as a line chart on a secondary y-axis

col6 = st.columns(1)[0]


fig3 = go.Figure()
fig3.add_trace(go.Bar(x = result1["State"], y = result1["TotalSales"], name = "Total Sales"))
fig3.add_trace(go.Scatter(x = result1["State"], y = result1["UnitsSold"], mode = "lines", name = "Units Sold", yaxis = "y2"))

fig3.update_layout(
    xaxis = dict(title="State"),
    yaxis = dict(title="Total Sales", showgrid = False),
    yaxis2= dict(title="Unit Sold", overlaying = "y", side = "right"),
    template = "gridon",
    legend = dict(x = 1, y = 1)
)

with col6:
    st.subheader("Total Sales and Unit Sold by State")
    st.plotly_chart(fig3, use_container_width=True)


view3, dwn3 = st.columns((2))

with view3:
    expander = st.expander("View Data for Sales by Units Sold")
    expander.write(result1)

with dwn3:
    st.download_button("Get Data", data = result1.to_csv().encode("utf-8"),
                       file_name = "Sales_by_UnitsSold.csv", mime="text/csv")
        
st.divider()

col7 = st.columns((1))

# TREE MAP  based on (Region, State, TotalSales)

st.subheader("Total Sales by Region and States in Treemap")
fig3 = px.treemap(filtered_df, path= ["Region", "State", "TotalSales"], values= "TotalSales", hover_data= ["TotalSales"],
                  color= "State")
fig3.update_layout(width= 800, height = 650)
st.plotly_chart(fig3)

with st.expander("View TreeMap Data"):
    st.write(filtered_df.style.background_gradient(cmap="Oranges"))
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Data", data= csv, file_name= "TreeMap.csv", mime= "text/csv",
                       help="Click Here to Download The Data as a CSV File")


view4, dwn4 = st.columns((2))

with view4:
    result2 = filtered_df[["Region", "City", "TotalSales"]].groupby(by=["Region", "City"])["TotalSales"].sum()
    expander = st.expander("view data for Total Sales by Region and City")
    expander.write(result2)

with dwn4:
    st.download_button("Get Data", data = result2.to_csv().encode("utf-8"),
                                        file_name="Sales_by_Region", mime="text.csv")
    

view5, dwn5 = st.columns((2))

with view5:
    expander = st.expander("View Sales Raw Data")
    expander.write(filtered_df)

with dwn5:
    st.download_button("Get Raw Data", data = filtered_df.to_csv().encode("utf-8"),
                       file_name = "SalesRawData.csv", mime="text/csv")
    
st.divider()