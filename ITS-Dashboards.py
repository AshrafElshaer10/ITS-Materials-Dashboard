import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import datetime as dt 
from numerize import numerize # Used to convert values into Thousands & Millions
from PIL import Image, ImageDraw
import time 

base="dark"

# Body
st.set_page_config (layout="wide")

# Define CSS style for title
title_style = """
<style>
    .title-text {
        text-align: center;
        font-size: 36px;
        font-weight: bold;
        color: #FFFFFF; /* Change color as needed */
        text-decoration: underline; /* Underline the text */
    }
    .title-frame {
        padding: 20px;
        background-color: #008080; /* Change background color as needed */
        border-radius: 10px; /* Add rounded corners */
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1); /* Add shadow effect */
    }
</style>
"""

# Display the CSS style
st.markdown(title_style, unsafe_allow_html=True)

# Display the title within a frame
st.markdown("""
    <div class="title-frame">
        <p class="title-text">  Materials & Earned Value Dashboard</p>
    </div>
""", unsafe_allow_html=True)

# Display the title
st.markdown('<p class="title-text"> </p>', unsafe_allow_html=True)

# Sidebar - Stage 01
st.sidebar.image(r"images.png", width=380)
st.write('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True) # Help to remove white space above Header
st.sidebar.header("📊   Financial Analysis", divider = 'violet')

st.subheader("Please Insert Your Materials Data [:red[Kindly check your inputs carefully before 'Submit']]:", divider='red') 

# Create a form
with st.form(key ="input_form", clear_on_submit= True): # "clear_on_submit" to remove inserted values & be ready for new vlaues
    # Creating Database Format
    Database = pd.DataFrame(index = None, columns=['Date/Time', 'Description', 'Part No.', 'Unit', 'Trade', 'Clause', 'Brand', 'Origin', 'Road', 'Location', 
                                                'Progress (%)', 'QTY._As _Per_Contract', 'BAC = Budget @ Completion (EGP)','Actual_QTY.', 'Actual_Unit_Cost(EGP)',
                                                'Targeted_Unit_Sale(EGP)'])
    # Change columns data types
    Database['Date/Time']=pd.to_datetime(Database['Date/Time'])
    Database[['Description','Part No.','Trade','Unit','Clause','Brand','Origin','Road','Location']] = Database[['Description','Part No.','Trade','Unit','Clause','Brand','Origin',
                                                                                                                'Road','Location']].astype(str)
    Database[['QTY._As _Per_Contract','Actual_QTY.','Actual_Unit_Cost(EGP)', 'Targeted_Unit_Sale(EGP)', 'BAC = Budget @ Completion (EGP)','Progress (%)']] = Database[['QTY._As _Per_Contract','Actual_QTY.','Actual_Unit_Cost(EGP)', 'Targeted_Unit_Sale(EGP)', 'BAC = Budget @ Completion (EGP)','Progress (%)']].astype(float)

    # Converting some attributes to a limited drop down list for validation purpose to act as user input
    edited_data = st.data_editor(Database, column_config={        
            "Trade": st.column_config.SelectboxColumn(
            options=["Electrical System", "Structure Cabling", "TMS", "Network System", "CCTV System", "Light Current System",
                     "HVAC System", "Monitoring System", "Video Wall System", "Furniture", "TCS"], width="medium"),
            "Unit": st.column_config.SelectboxColumn(
            options=["Mtr.", "PC."], width="medium"),
            "Clause": st.column_config.SelectboxColumn(
            options=["PWR Cables", "1st Fix devices", "3rd Fix devices", "PWR Cable Trays", "Data Cable Trays", "Elec. Panels", "Raceways", "Earthing",
                     "Gen. Set", "TMS", "IP telephones", "Network", "Data Racks", "Data cables", "CCTV", "Fire Alarm",
                     "Fire Fighting", "Access Control", "HVAC", "Work Station", "Video Wall", "Furniture", "UPS", "Structure Cabling", 
                     "EMT Devices", "Infrastructure", "TCS"], width="medium"),
            "Brand": st.column_config.SelectboxColumn(
                options=["Elsewedy Cables", "New Ega", "Legrand", "Egytray", "Lectro", "Elsharif", "Local", "Erico - Mega Electric",
                     "kohler - Tawakol", "AUTOSTRADA", "AVAYA", "Huawei", "PANDUIT", "AXIS", "SUPREMA", "CARRIER",
                     "DELL", "BARCO", "BARCO Intertech", "KIT DISPLAY", "Multinet/Corning", "Future Electric", "ABB", "NASSAR TECH", 
                     "ITALY", "SHALON", "POS EGYPT","AUTOSTRADA / Other", "CORNING / PANDUIT", "CORNING","ASF / GHAZALA", "NOVO", "GERGES", "CAIRO", "Cardinal"], width="medium"),
            "Origin": st.column_config.SelectboxColumn(
            options=["Local", "Foreign"], width="medium"),
            "Road": st.column_config.SelectboxColumn(
            options=["Shobra Benha", "Cairo Ismailia", "Cairo Sokhna", "Cairo Suez", "Cairo Alex", "Regional Ring Road", "Ring Road", "Middle Ring Road"], width="medium"),
            "Location": st.column_config.SelectboxColumn(
            options=["General", "RCP-01 Room", "RCP-02 Room", "Server Room", "TMP Room", "Module A 3 lanes", "Module A 4 lanes", "Module A 5 lanes",
                     "Module A 6 lanes", "Module A 7 lanes", "Module A 8 lanes", "Module A 9 lanes", "Module A 10 lanes", "Module A 11 lanes", "T1 WIM 1 lane", 
                     "T2 WIM 2 lane", "T3 WIM 3 lane", "A4 WIM for 4 lanes", "A5 WIM for 5 lanes", "A6 WIM for 6 lanes", 
                     "A7 WIM for 7 lanes", "Poles", "Toll Plaza"], width="medium"),
            "Progress (%)": st.column_config.SelectboxColumn(
            options=["0.0", "0.50", "0.75", "1.00"], width="medium"), # All above was configured columns with drop down list, "required" parameter set to "True" to prevent adding records with null values. 
            }, height=250, num_rows="dynamic")
          
    # Read Existed Database to append on it
    Database = pd.read_csv(r"Data_Store.csv")
    # Append the edited data to the existing database
    database_without_calculations = pd.concat([Database, edited_data], ignore_index=True)
    # Apply Calculations to get targeted columns
    # edited_data['Date/Time'] = dt.datetime.now()
    ## Convert the relevant columns to numeric types using {pd.to_numeric()}
    database_without_calculations['Actual_QTY.'] = pd.to_numeric(database_without_calculations['Actual_QTY.'], errors='coerce') # Generated by AI after string substraction error obtained
    database_without_calculations['QTY._As _Per_Contract'] = pd.to_numeric(database_without_calculations['QTY._As _Per_Contract'], errors='coerce') # Generated by AI after string substraction error obtained
    database_without_calculations['Qty._Variance'] = (database_without_calculations['Actual_QTY.'] - database_without_calculations['QTY._As _Per_Contract']).round(2)
    database_without_calculations['Targeted_Unit_Sale(EGP)'] = pd.to_numeric(database_without_calculations['Targeted_Unit_Sale(EGP)'], errors='coerce') # Generated by AI after string substraction error obtained
    database_without_calculations['Total_Targeted_Sales(EGP)'] = (database_without_calculations['QTY._As _Per_Contract'] * database_without_calculations['Targeted_Unit_Sale(EGP)']).round(2)
    database_without_calculations['Total_Expected_Sales(EGP)'] = (database_without_calculations['Actual_QTY.'] * database_without_calculations['Targeted_Unit_Sale(EGP)']).round(2)
    database_without_calculations['Sales_Variance(EGP)'] = (database_without_calculations['Qty._Variance'] * database_without_calculations['Targeted_Unit_Sale(EGP)']).round(2)
    database_without_calculations['Actual_Unit_Cost(EGP)'] = pd.to_numeric(database_without_calculations['Actual_Unit_Cost(EGP)'], errors='coerce')
    database_without_calculations['QTY._As _Per_Contract'] = pd.to_numeric(database_without_calculations['QTY._As _Per_Contract'], errors='coerce')
    database_without_calculations['AC = Actual_Cost_To_Date(EGP)'] = (database_without_calculations['Actual_Unit_Cost(EGP)'] * database_without_calculations['Actual_QTY.']).round(2)
    database_without_calculations['BAC = Budget @ Completion (EGP)'] = pd.to_numeric(database_without_calculations['BAC = Budget @ Completion (EGP)'], errors='coerce')
    database_without_calculations['Progress (%)'] = pd.to_numeric(database_without_calculations['Progress (%)'], errors='coerce')
    database_without_calculations['EV = Earned Value (EGP)'] = (database_without_calculations['BAC = Budget @ Completion (EGP)'] * database_without_calculations['Progress (%)']).round(2)
    database_without_calculations['CPI = Cost Performance index'] = (database_without_calculations['EV = Earned Value (EGP)'] / database_without_calculations['AC = Actual_Cost_To_Date(EGP)']).round(2)
    database_without_calculations['CV = Cost Variance (EGP)'] = (database_without_calculations['EV = Earned Value (EGP)'] - database_without_calculations['AC = Actual_Cost_To_Date(EGP)']).round(2)
    database_without_calculations['TCPI = To Complete Performance index'] = ((database_without_calculations['BAC = Budget @ Completion (EGP)'] - database_without_calculations['EV = Earned Value (EGP)'])/(database_without_calculations['BAC = Budget @ Completion (EGP)'] - database_without_calculations['AC = Actual_Cost_To_Date(EGP)'])).round(2)
    database_without_calculations['EAC = Estimated @ Completion (EGP)'] = (database_without_calculations['AC = Actual_Cost_To_Date(EGP)'] + database_without_calculations['BAC = Budget @ Completion (EGP)'] - database_without_calculations['EV = Earned Value (EGP)']).round(2)
    database_without_calculations['ETC = Estimate Cost to complete (EGP)'] = (database_without_calculations['EAC = Estimated @ Completion (EGP)'] - database_without_calculations['AC = Actual_Cost_To_Date(EGP)']).round(2)
    database_without_calculations['VAC = Variance @ Completion (EGP)'] = (database_without_calculations['BAC = Budget @ Completion (EGP)'] - database_without_calculations['EAC = Estimated @ Completion (EGP)']).round(2)
    database_without_calculations['Total_Targeted_Gross_Profit(EGP)'] = (database_without_calculations['Total_Targeted_Sales(EGP)'] - database_without_calculations['BAC = Budget @ Completion (EGP)']).round(2)
    database_without_calculations['Total_Expected_Gross_Profit(EGP)'] = (database_without_calculations['Total_Expected_Sales(EGP)'] - database_without_calculations['EAC = Estimated @ Completion (EGP)']).round(2)
    database_without_calculations['Actual_Sales_Progress(EGP)'] = (database_without_calculations['Total_Expected_Sales(EGP)'] * database_without_calculations['Progress (%)']).round(2)
    database_without_calculations['Actual_To_Date_Profit (EGP)'] = (database_without_calculations['Actual_Sales_Progress(EGP)'] - database_without_calculations['AC = Actual_Cost_To_Date(EGP)']).round(2)
    database_without_calculations['Cash_in(EGP)'] = 0 # Generating column as below indexing through iloc can not be defined without base
    database_without_calculations['Cash_out(EGP)'] = 0 # Generating column as below indexing through iloc can not be defined without base
    if len(database_without_calculations) > 0:    # Return No. of rows
        database_without_calculations['Cash_in(EGP)'].iloc[0] = database_without_calculations['Actual_Sales_Progress(EGP)'].iloc[0] # As 1st item hasn't previous value to accumulate
        database_without_calculations['Cash_out(EGP)'].iloc[0] = database_without_calculations['AC = Actual_Cost_To_Date(EGP)'].iloc[0] # As 1st item hasn't previous value to accumulate    
    for i in range(1, len(database_without_calculations['Description'])):
        database_without_calculations['Cash_in(EGP)'].iloc[i] = database_without_calculations['Cash_in(EGP)'].iloc[i-1] + database_without_calculations['Actual_Sales_Progress(EGP)'].iloc[i]
        database_without_calculations['Cash_out(EGP)'].iloc[i] = database_without_calculations['Cash_out(EGP)'].iloc[i-1] + database_without_calculations['AC = Actual_Cost_To_Date(EGP)'].iloc[i]  
    
    # Create the submit button
    Submit = st.form_submit_button("Submit")
    if Submit:
        with st.spinner('Wait for it...'):
            time.sleep(5)
        # Validate the edited data
        if (edited_data['Date/Time'].isna().any() or
            edited_data['Description'].isna().any() or
            edited_data['Part No.'].isna().any() or
            edited_data['Unit'].isna().any() or
            edited_data['Trade'].isna().any() or
            edited_data['Clause'].isna().any() or
            edited_data['Brand'].isna().any() or
            edited_data['Origin'].isna().any() or
            edited_data['Road'].isna().any() or
            edited_data['Location'].isna().any() or
            edited_data['Progress (%)'].isna().any() or
            edited_data['QTY._As _Per_Contract'].isna().any() or
            edited_data['BAC = Budget @ Completion (EGP)'].isna().any() or
            edited_data['Actual_QTY.'].isna().any() or
            edited_data['Actual_Unit_Cost(EGP)'].isna().any() or
            edited_data['Targeted_Unit_Sale(EGP)'].isna().any()):
            st.warning("Please fill-in all missing fields as shown below, without fullfilling all values it cannot be submitted!")
            null_rows = edited_data[edited_data.isnull().any(axis=1)]

            # Conditional formatting for "None" values
            def format_none(val):
                if val is None:
                    return 'background-color: rgba(210, 109, 109, 1); color: rgba(0, 0, 0, 0)'
                else:
                    return ''
            # Apply the conditional formatting to the DataFrame
            styled_null_rows = null_rows.style.applymap(format_none)

            # Display the styled DataFrame
            st.write(styled_null_rows, unsafe_allow_html=True)

        else:
            # Export Final database to the CSV file
            database_without_calculations.to_csv(r"Data_Store.csv", index=False)
            # edited_data = edited_data.drop(edited_data.index) # Data may be duplicated after submit without inserting new values, but duplication will be removed as soon as rerun
            st.success("Congratulation, Your Data have been already submitted!")     
    else:
        st.info("Please Insert New Data, then press 'Submit'")

# Show Updated Database
st.subheader("Existed Database")
Updated_Database = pd.read_csv(r"Data_Store.csv")
Updated_Database

# Exploration & Cleaning Stage
st.header("Duplicated Records Exploration & Cleaning Stage:", divider= 'red')

## define functions to for show, remove or ignore duplications once called
def show_duplicates():
    st.warning("Please check the below duplicated values before dropping (if required):")
    duplicates = Updated_Database[Updated_Database.duplicated(keep = False, subset=['Description', 'Part No.', 'Unit', 'Trade', 'Clause', 'Brand', 
                                    'Origin', 'Road', 'Location', 'Progress (%)', 'QTY._As _Per_Contract', 'BAC = Budget @ Completion (EGP)',
                                    'Actual_QTY.', 'Actual_Unit_Cost(EGP)', 'Targeted_Unit_Sale(EGP)'])]
    st.write(duplicates)

def drop_duplicates():
    global Updated_Database
    duplicates = Updated_Database[Updated_Database.duplicated(keep = False, subset=['Description', 'Part No.', 'Unit', 'Trade', 'Clause', 'Brand', 
                                    'Origin', 'Road', 'Location', 'Progress (%)', 'QTY._As _Per_Contract', 'BAC = Budget @ Completion (EGP)',
                                    'Actual_QTY.', 'Actual_Unit_Cost(EGP)', 'Targeted_Unit_Sale(EGP)'])]    
    
    # Add a checkbox column to the duplicates DataFrame
    duplicates['Select'] = False
    
    # Display the duplicates DataFrame with the checkbox column
    selected_rows = st.data_editor(duplicates, column_order = ('Select','Date/Time','Description', 'Part No.', 'Unit', 'Trade', 'Clause', 'Brand', 
                                    'Origin', 'Road', 'Location', 'Progress (%)', 'QTY._As _Per_Contract', 'BAC = Budget @ Completion (EGP)',
                                    'Actual_QTY.', 'Actual_Unit_Cost(EGP)', 'Targeted_Unit_Sale(EGP)'),   column_config={"Select": st.column_config.CheckboxColumn("Duplicated_Records",
                                                                help="Select your Duplicated columns needs to be **dropped**",
                                                                default=False)},hide_index=False)
    # Get the selected rows
    selected_indexes = selected_rows[selected_rows['Select']].index.tolist()
    
    
    if st.button('Drop Selected Rows'):
        # Drop the selected rows from the original Updated_Database
        Updated_Database = Updated_Database.drop(selected_indexes)
        st.success("Congratulation, All duplicated values had been removed!, Please check below:")
        st.write('Updated Database after removal:')
        st.write(Updated_Database)    
        return Updated_Database   
    return Updated_Database

def main():
    global Updated_Database
    if 'button_clicked' not in st.session_state:
        st.session_state.button_clicked = None
                
    if st.session_state.button_clicked == 'Show_Duplicates':
        show_duplicates()
    elif st.session_state.button_clicked == 'Drop_duplicates':
        drop_duplicates()

btn1, btn2, btn3 = st.columns(3)
if btn1.button("Show Duplicates"):
    st.session_state.button_clicked = 'Show_Duplicates'

if btn2.button("Select Duplicates need to be removed"):
    st.session_state.button_clicked = 'Drop_duplicates'

if __name__ == "__main__":
    main()

st.divider()

Updated_Database.to_csv(r"Data_Store.csv", index=False) 

# Creating Metrics Cards
st.header("Project Metrics & KPI's", divider = 'red')
# Define Roads selector to show metrics on one or more roads
st.markdown("#### [*Please select one or more roads:*]", unsafe_allow_html=True)
# Create unique list of options 
road_selector = st.multiselect("", ["All","Shobra Benha", "Cairo Ismailia", "Cairo Sokhna",
                                "Cairo Suez", "Cairo Alex", "Regional Ring Road", "Ring Road", "Middle Ring Road"], default= "All")
if "All" in road_selector:
    road_selector = ["Shobra Benha", "Cairo Ismailia", "Cairo Sokhna",
                     "Cairo Suez", "Cairo Alex", "Regional Ring Road", "Ring Road", "Middle Ring Road"]

   
# Apply indexing on main Updated_Database based on pre-defined unique list
filtered_road_data = Updated_Database[Updated_Database['Road'].isin(road_selector)] # Vertical Filtering

# Redefine updated Updated_Database as below filteration can not be applied on non defined because all variables inside with form cannot be global
Updated_Database= pd.read_csv(r"Data_Store.csv")

a1_metric_value = filtered_road_data['BAC = Budget @ Completion (EGP)'] # Horizontal Filtering
a2_metric_value = filtered_road_data['AC = Actual_Cost_To_Date(EGP)'] # Horizontal Filtering
a3_metric_value = filtered_road_data['EAC = Estimated @ Completion (EGP)'] # Horizontal Filtering
a4_metric_value = filtered_road_data['EV = Earned Value (EGP)'] # Horizontal Filtering
a5_metric_value = filtered_road_data['CV = Cost Variance (EGP)'] # Horizontal Filtering
a6_metric_value = filtered_road_data['VAC = Variance @ Completion (EGP)'] # Horizontal Filtering
b1_metric_value = filtered_road_data['ETC = Estimate Cost to complete (EGP)'] # Horizontal Filtering
b2_metric_value = filtered_road_data['CPI = Cost Performance index'] # Horizontal Filtering
b3_metric_value = filtered_road_data['TCPI = To Complete Performance index'] # Horizontal Filtering
b4_metric_value = filtered_road_data['Total_Targeted_Gross_Profit(EGP)'] # Horizontal Filtering
b5_metric_value = filtered_road_data['Actual_To_Date_Profit (EGP)'] # Horizontal Filtering
b6_metric_value = filtered_road_data['Progress (%)'] # Horizontal Filteringst

a1, a2, a3, a4, a5, a6 = st.columns(6, gap = "small")
b1, b2, b3, b4, b5, b6 = st.columns(6, gap = "small")

# define delta values for conditional formating
cv_delta = round(a5_metric_value.sum(), 2)
vac_delta = round(a6_metric_value.sum(), 2)
CPI_delta = f"{round((b2_metric_value.mean() - 1)*100, 2)}%"
TCPI_delta = f"{round((b3_metric_value.mean() - 1)*100 , 1)}%"

# st.latex(r'''left(\frac{1-r^{n}}{1-r}\right)''')
# a3_help = st.latex(r'''AC + BAC - EV''')

# 1st Row - Please note that 
a1_metric_value_sum = a1_metric_value.sum()
a1_metric_value_rounded = round(a1_metric_value_sum, 2)
a1.metric(':moneybag: [BAC] :gray-background[Budget @ Comp. (EGP)]', numerize.numerize(a1_metric_value_rounded), help ="The value of total planned work, the project cost baseline")
a2_metric_value_sum = a2_metric_value.sum()
a2_metric_value_rounded = round(a2_metric_value_sum, 2)
a2.metric('💸[AC] :gray-background[Actual Cost To Date (EGP)]', numerize.numerize(a2_metric_value_rounded), help ="The actual cost of all the work completed to a point in time, usually the data date")
a3_metric_value_sum = a3_metric_value.sum()
a3_metric_value_rounded = round(a3_metric_value_sum, 2)
a3.metric(':credit_card: [EAC] :gray-background[Estimated cost @ Completion (EGP)]', numerize.numerize(a3_metric_value_rounded), help = "If future work will be accomplished at the planned rate \t :violet[(EAC = AC + BAC - EV)]")
a4_metric_value_sum = a4_metric_value.sum()
a4_metric_value_rounded = round(a4_metric_value_sum, 2)
a4.metric(':chart: [EV] :gray-background[Earned Value (EGP)]', numerize.numerize(a4_metric_value_rounded), help ="The planned value of all the work completed (earned) to a point in time, usually the data date, without reference to actual costs")
a5_metric_value_sum = a5_metric_value.sum()
a5_metric_value_rounded = round(a5_metric_value_sum, 2)
cv_delta = numerize.numerize(cv_delta)
a5.metric(':bar_chart: [CV] :gray-background[Cost Variance (EGP)]', numerize.numerize(a5_metric_value_rounded), delta = cv_delta, delta_color='normal', help ="Positive = Under planned cost, Neutral = On planned cost, Negative = Over planned cost \t :violet[(CV = EV-AC)]")
a6_metric_value_sum = a6_metric_value.sum()
a6_metric_value_rounded = round(a6_metric_value_sum, 2)
vac_delta = numerize.numerize(vac_delta)
a6.metric(':briefcase: [VAC] :gray-background[Variance @ Completion (EGP)]', numerize.numerize(a6_metric_value_rounded), delta = vac_delta, delta_color='normal', help = "Positive = Under planned cost, Neutral = On planned cost, Negative = Over planned cost \t :violet[(VAC = BAC-EAC)]")

# 2nd Row
b1_metric_value_sum = b1_metric_value.sum()
b1_metric_value_rounded = round(b1_metric_value_sum, 2)
b1.metric(':dollar: [ETC] :gray-background[Estimate Cost to complete (EGP)]', numerize.numerize(b1_metric_value_rounded), help = "The expected cost to finish all the remaining project work \t :violet[(ETC = EAC-AC)]")
b2_metric_value_mean = b2_metric_value.mean()
b2_metric_value_rounded = round(b2_metric_value_mean, 2)
b2.metric(':card_index: [CPI] :gray-background[Cost Performance index]', b2_metric_value_rounded, delta = CPI_delta, delta_color='normal', help ="Greater than 1.0 = Under planned cost, Exactly 1.0 = On planned cost, Less than 1.0 = Over planned cost \t :violet[(CPI = EV/AC)]")
b3_metric_value_mean = b3_metric_value.mean()
b3_metric_value_rounded = round(b3_metric_value_mean, 2)
b3.metric(':card_index_dividers: [TCPI] :gray-background[To Complete Performance index]', b3_metric_value_rounded, delta = TCPI_delta, delta_color='normal', help ="Greater than 1.0 = Harder to complete, Exactly 1.0 = Same to complete, Less than 1.0 = Easier to complete \t :violet[TCPI = (BAC-EV)/(BAC-AC)]")
b4_metric_value_sum = b4_metric_value.sum()
b4_metric_value_rounded = round(b4_metric_value_sum, 2)
b4.metric(':dart: [Target Profit(EGP)] :gray-background[Total_Targeted_Gross_Profit(EGP)]', numerize.numerize(b4_metric_value_rounded), help = "The value of total planned caluses profit, the project profit baseline")
b5_metric_value_sum = b5_metric_value.sum()
b5_metric_value_rounded = round(b5_metric_value_sum, 2)
b5.metric(':heavy_dollar_sign: [To_Date_Profit(EGP)] :gray-background[Actual_To_Date_Profit (EGP)]', numerize.numerize(b5_metric_value_rounded), help = "Actual Obtained Profit")
b6_metric_value_mean = b6_metric_value.mean()
b6_metric_value_rounded = round(b6_metric_value_mean, 2)
b6.metric('⌛[Overall_Work_Completion_Progress] :gray-background[(%)]', (b6_metric_value_rounded*100))

# Sidebar - Stage 02
# Creating A guage plot showing relation between To_Date profit & Expected profit 
fig7 = go.Figure(go.Indicator(
    domain={'x': [0, 0.9], 'y': [0.1, 1]},
    value=Updated_Database['Actual_To_Date_Profit (EGP)'].sum(),
    mode="gauge+number+delta",
    title={'text': "Overall Profit Indicator",
           'font_size': 30,
           'font_color': 'white'},
    delta={'reference': Updated_Database['Total_Targeted_Gross_Profit(EGP)'].sum()},
    number= {'font_color':'green',
             'font_size': 30},
    gauge={'axis': {'range': [None, Updated_Database['Total_Expected_Gross_Profit(EGP)'].sum()]},
           'steps': [{'range': [0, Updated_Database['Total_Expected_Gross_Profit(EGP)'].sum()], 'color': "lightgray"}],
           'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75,
                         'value': Updated_Database['Total_Targeted_Gross_Profit(EGP)'].sum()},
           'bar': {'color': 'green'}}))

# Add additional traces with names
fig7 = go.Figure(go.Indicator(
    domain={'x': [0, 0.9], 'y': [0.1, 1]},
    value=Updated_Database['Actual_To_Date_Profit (EGP)'].sum(),
    mode="gauge+number+delta",
    title={'text': "Overall Profit Indicator",
           'font_size': 30,
           'font_color': 'white'},
    delta={'reference': Updated_Database['Total_Targeted_Gross_Profit(EGP)'].sum()},
    number= {'font_color':'green',
             'font_size': 30},
    gauge={'axis': {'range': [None, Updated_Database['Total_Expected_Sales(EGP)'].sum()]},
           'steps': [{'range': [0, Updated_Database['Total_Expected_Gross_Profit(EGP)'].sum()], 'color': "lightgray"}],
           'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75,
                         'value': Updated_Database['Total_Targeted_Gross_Profit(EGP)'].sum()},
           'bar': {'color': 'green'}}))

# Add additional traces with names
fig7.add_trace(go.Indicator(
    value=Updated_Database['Total_Targeted_Gross_Profit(EGP)'].sum(),
    delta={'reference': Updated_Database['Total_Expected_Sales(EGP)'].sum()},
    number= {'font_color':'red',
             'font_size': 30},
    #domain={'x': [0.6 , 0.95], 'y': [0.35 , 0.9]},
    name='Total_Targeted_Gross_Profit(EGP)'))

fig7.add_trace(go.Indicator(
    value=Updated_Database['Total_Expected_Sales(EGP)'].sum(),
    number= {'font_color':'white',
             'font_size': 30},
    domain={'x': [0.75 , 0.9], 'y': [0.15, 0.5]},
    name='Total_Expected_Sales(EGP)'))

fig7.add_trace(go.Indicator(
    value=Updated_Database['Total_Expected_Gross_Profit(EGP)'].sum(),
    number= {'font_color':'lightgrey',
             'font_size': 30},
    domain={'x': [0, 0.9], 'y': [0.5, 0.6]},
    name='Total_Expected_Gross_Profit(EGP)'))

# Change Figure-07 format
fig7.update_layout(showlegend=True, # Show the legend
    margin=dict(l=0, r=0, b=0, t=0, pad=0),  # Margins used to remove all unused spaces  
    legend=dict(
        x=0.1,
        y=0.9,
        traceorder="normal",
        font=dict(
            family="sans-serif",
            size=12,
            color="black"
        ),
        bgcolor="LightSteelBlue",
        bordercolor="White",
        borderwidth=2  # Set the spacing between legend groups
                )
                    )

# Plot Figures-07
st.sidebar.plotly_chart(fig7)

# Plot Legend for profit indicator
def draw_rounded_rect(width, height, corner_radius, color):
    # Create a new image with transparent background
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Draw the rounded rectangle
    draw.rounded_rectangle((0, 0, width, height), corner_radius, fill=color)

    return image

# Set shapes colors
CP1_color = (0, 80 , 0, 250)  # Green color in RGBA format
CP2_color = (210, 215 , 211, 255)  # Grey color in RGBA format
CP3_color = (255, 0 , 0, 255)  # Red color in RGBA format

# Draw the rounded rectangles
image1 = draw_rounded_rect(100, 25, 0, CP1_color)
image2 = draw_rounded_rect(100, 25, 0, CP2_color)
image3 = draw_rounded_rect(100, 5, 0, CP3_color)

# Display the images in the sidebar
with st.sidebar:
    st.header("🚥 Profit Indicator Legend:", divider='violet')
    col1, col2, col3 = st.columns(3)
    col1.image(image1, caption="Actual Profit (EGP)")
    col2.image(image2, caption="Expected Profit (EGP)")
    col3.image(image3, caption="Target Profit (EGP)")

#Subheader
st.sidebar.header('⌛ Road/s Progress(%)', divider = 'violet')
# Define Roads Progress (%)
Shobra_Benha_progress = Updated_Database[Updated_Database['Road']=='Shobra Benha']['Progress (%)'].mean()*100
Cairo_Ismailia_progress = Updated_Database[Updated_Database['Road']=='Cairo Ismailia']['Progress (%)'].mean()*100
Cairo_Alex_progress = Updated_Database[Updated_Database['Road']=='Cairo Alex']['Progress (%)'].mean()*100
Cairo_Sokhna_progress = Updated_Database[Updated_Database['Road']=='Cairo Sokhna']['Progress (%)'].mean()*100
Cairo_Suez_progress = Updated_Database[Updated_Database['Road']=='Cairo Suez']['Progress (%)'].mean()*100
Ring_Road_progress = Updated_Database[Updated_Database['Road']=='Ring Road']['Progress (%)'].mean()*100
Middle_Ring_Road_progress = Updated_Database[Updated_Database['Road']=='Middle Ring Road']['Progress (%)'].mean()*100
Regional_Ring_Road_progress = Updated_Database[Updated_Database['Road']=='Regional Ring Road']['Progress (%)'].mean()*100
All_Roads_progress = Updated_Database['Progress (%)'].mean()*100

# Divide Page
d01, d02 = st.sidebar.columns(2)
d11, d12 = st.sidebar.columns(2)
d21, d22 = st.sidebar.columns(2)
d31, d32 = st.sidebar.columns(2)
d41, d42 = st.sidebar.columns(2)

with d01:
    # creating a figure has pie format divided into two portions the first represent progress & the other represent remaining, each of them named & colored
    fig10 = px.pie(Updated_Database, values = [Shobra_Benha_progress, 100 - Shobra_Benha_progress], names = ['Progress (%)',"remaining"], hole = 0.5,
            color_discrete_sequence = ['green', 'lightgrey'], height=200, width=200
            )
    # Inner donut Specs
    fig10.update_traces(textfont_size=15, title_position = 'bottom center', title = "Shobra Benha Prog.(%)", title_font_size=15, title_font_color='white')
    # Change Figure-10 format
    fig10.update_layout(legend= {'font': {'size':12,
                                 'color':'white'},
                                 'x':0.25,'y': -5},
                        margin =dict( 
                                l=0,
                                r=0,
                                b=0,
                                t=0,
                                pad=0)) # Margins used to remove all unused spaces
    st.plotly_chart(fig10)

with d02:
    # creating a figure has pie format divided into two portions the first represent progress & the other represent remaining, each of them named & colored
    fig11 = px.pie(Updated_Database, values = [Cairo_Ismailia_progress, 100 - Cairo_Ismailia_progress], names = ['Progress (%)',"remaining"], hole = 0.5,
            color_discrete_sequence = ['green', 'lightgrey'], height=200, width=200
            )
    # Inner donut Specs
    fig11.update_traces(textfont_size=15, title_position = 'bottom center', title = 'Cairo Ismailia Prog.(%)', title_font_size=15, title_font_color='white')
    # Change Figure-11 format
    fig11.update_layout(legend= {'font': {'size':12,
                                 'color':'white'},
                                 'x':0.25,'y': -5},
                        margin = dict( 
                                l=0,
                                r=0,
                                b=0,
                                t=0,
                                pad=0)) # Margins used to remove all unused spaces
    st.plotly_chart(fig11)

with d11:
    # creating a figure has pie format divided into two portions the first represent progress & the other represent remaining, each of them named & colored
    fig12 = px.pie(Updated_Database, values = [Cairo_Alex_progress, 100 - Cairo_Alex_progress], names = ['Progress (%)',"remaining"], hole = 0.5,
            color_discrete_sequence = ['green', 'lightgrey'], height=200, width=200
            )
    # Inner donut Specs
    fig12.update_traces(textfont_size=15, title_position = 'bottom center', title = "Cairo Alex Prog.(%)", title_font_size=15, title_font_color='white')
    # Change Figure-10 format
    fig12.update_layout(legend= {'font': {'size':12,
                                 'color':'white'},
                                 'x':0.25,'y': -5},
                        margin = dict( 
                                l=0,
                                r=0,
                                b=0,
                                t=0,
                                pad=0)) # Margins used to remove all unused spaces
    st.plotly_chart(fig12)

with d12:
    # creating a figure has pie format divided into two portions the first represent progress & the other represent remaining, each of them named & colored
    fig13 = px.pie(Updated_Database, values = [Cairo_Sokhna_progress, 100 - Cairo_Sokhna_progress], names = ['Progress (%)',"remaining"], hole = 0.5,
            color_discrete_sequence = ['green', 'lightgrey'], height=200, width=200
            )
    # Inner donut Specs
    fig13.update_traces(textfont_size=15, title_position = 'bottom center', title = 'Cairo Sokhna Prog.(%)', title_font_size=15, title_font_color='white')
    # Change Figure-11 format
    fig13.update_layout(legend= {'font': {'size':12,
                                 'color':'white'},
                                 'x':0.25,'y': -5},
                        margin = dict( 
                                l=0,
                                r=0,
                                b=0,
                                t=0,
                                pad=0)) # Margins used to remove all unused spaces
    st.plotly_chart(fig13)

with d21:
    # creating a figure has pie format divided into two portions the first represent progress & the other represent remaining, each of them named & colored
    fig14 = px.pie(Updated_Database, values = [Cairo_Suez_progress, 100 - Cairo_Suez_progress], names = ['Progress (%)',"remaining"], hole = 0.5,
            color_discrete_sequence = ['green', 'lightgrey'], height=200, width=200
            )
    # Inner donut Specs
    fig14.update_traces(textfont_size=15, title_position = 'bottom center', title = "Cairo Suez Prog.(%)", title_font_size=15, title_font_color='white')
    # Change Figure-10 format
    fig14.update_layout(legend= {'font': {'size':12,
                                 'color':'white'},
                                 'x':0.25,'y': -5},
                        margin = dict( 
                                l=0,
                                r=0,
                                b=0,
                                t=0,
                                pad=0)) # Margins used to remove all unused spaces
    st.plotly_chart(fig14)

with d22:
    # creating a figure has pie format divided into two portions the first represent progress & the other represent remaining, each of them named & colored
    fig15 = px.pie(Updated_Database, values = [Ring_Road_progress, 100 - Ring_Road_progress], names = ['Progress (%)',"remaining"], hole = 0.5,
            color_discrete_sequence = ['green', 'lightgrey'], height=200, width=200
            )
    # Inner donut Specs
    fig15.update_traces(textfont_size=15, title_position = 'bottom center', title = 'Ring Road Prog.(%)', title_font_size=15, title_font_color='white')
    # Change Figure-11 format
    fig15.update_layout(legend= {'font': {'size':12,
                                 'color':'white'},
                                 'x':0.25,'y': -5},
                        margin = dict( 
                                l=0,
                                r=0,
                                b=0,
                                t=0,
                                pad=0)) # Margins used to remove all unused spaces
    st.plotly_chart(fig15)

with d31:
    # creating a figure has pie format divided into two portions the first represent progress & the other represent remaining, each of them named & colored
    fig16 = px.pie(Updated_Database, values = [Middle_Ring_Road_progress, 100 - Middle_Ring_Road_progress], names = ['Progress (%)',"remaining"], hole = 0.5,
            color_discrete_sequence = ['green', 'lightgrey'], height=200, width=200
            )
    # Inner donut Specs
    fig16.update_traces(textfont_size=15, title_position = 'bottom center', title = "Middle Ring Road Prog.(%)", title_font_size=15, title_font_color='white')
    # Change Figure-10 format
    fig16.update_layout(legend= {'font': {'size':12,
                                 'color':'white'},
                                 'x':0.25,'y': -5},
                        margin = dict( 
                                l=0,
                                r=0,
                                b=0,
                                t=0,
                                pad=0)) # Margins used to remove all unused spaces
    st.plotly_chart(fig16)

with d32:
    # creating a figure has pie format divided into two portions the first represent progress & the other represent remaining, each of them named & colored
    fig17 = px.pie(Updated_Database, values = [Regional_Ring_Road_progress, 100 - Regional_Ring_Road_progress], names = ['Progress (%)',"remaining"], hole = 0.5,
            color_discrete_sequence = ['green', 'lightgrey'], height=200, width=200
            )
    # Inner donut Specs
    fig17.update_traces(textfont_size=15, title_position = 'bottom center', title = 'Regional Ring Road Prog.(%)', title_font_size=15, title_font_color='white')
    # Change Figure-11 format
    fig17.update_layout(legend= {'font': {'size':12,
                                 'color':'white'},
                                 'x':0.25,'y': -5},
                        margin = dict( 
                                l=0,
                                r=0,
                                b=0,
                                t=0,
                                pad=0)) # Margins used to remove all unused spaces
    st.plotly_chart(fig17)

with d41:
    # creating a figure has pie format divided into two portions the first represent progress & the other represent remaining, each of them named & colored
    fig18 = px.pie(Updated_Database, values = [All_Roads_progress, 100 - All_Roads_progress], names = ['Progress (%)',"remaining"], hole = 0.5,
            color_discrete_sequence = ['green', 'lightgrey'], height=400, width=400
            )
    # Inner donut Specs
    fig18.update_traces(textfont_size=15, title_position = 'bottom center', title = "All Roads Prog.(%)", title_font_size=15, title_font_color='white')
    # Change Figure-10 format
    fig18.update_layout(legend= {'font': {'size':12,
                                 'color':'white'},
                                 'x':0.35,'y': -5},
                        margin =dict( 
                                l=0,
                                r=0,
                                b=0,
                                t=0,
                                pad=0)) # Margins used to remove all unused spaces
    st.plotly_chart(fig18)

st.divider()
# SubHeader
st.header("[Relation Between Numerical Values Per Road]", divider = 'red')
# Define Roads selector to show metrics on one or more roads
st.markdown("#### [*Please select one or more numerical attribute:*]", unsafe_allow_html=True)

# Multi Selector for numerical values
Nuemrical_Filter0 = st.multiselect('', ['Actual_QTY.','QTY._As _Per_Contract','Qty._Variance','Targeted_Unit_Sale(EGP)','Total_Targeted_Sales(EGP)',
                                   'Total_Expected_Sales(EGP)','Sales_Variance(EGP)','Actual_Unit_Cost(EGP)','QTY._As _Per_Contract','AC = Actual_Cost_To_Date(EGP)',
                                   'BAC = Budget @ Completion (EGP)','Progress (%)','EV = Earned Value (EGP)','CPI = Cost Performance index','CV = Cost Variance (EGP)',
                                   'TCPI = To Complete Performance index','EAC = Estimated @ Completion (EGP)','ETC = Estimate Cost to complete (EGP)',
                                   'VAC = Variance @ Completion (EGP)','Total_Targeted_Gross_Profit(EGP)','Total_Expected_Gross_Profit(EGP)','Actual_Sales_Progress(EGP)',
                                   'Actual_To_Date_Profit (EGP)'])

# Creating A chart showing a relation between EV, AC, CV per road
fig1 = px.histogram(Updated_Database, x='Road', y=Nuemrical_Filter0, height=500, width=1500, text_auto=True, barmode="group")
## Please note that using histogram instead of bar chart to solve a problem related to multi segments for each bar

# Show Data Labels & update properties
fig1.update_traces(textfont_size=80, textangle=0, textposition="auto", textfont_color= "white") #This will tell plotly that you want the display of y values in the format .2f meaning 2 decimal places after the decimal point

# Change Figure-01 format
fig1.update_layout(
    plot_bgcolor="rgba(85, 104, 225, 0.15)",
    legend_title= {'text': 'Legend',
                   'font': {'size': 15,
                            'color':'white'}},
    legend= {'font': {'size':12,
                      'color':'white'},
                      'x':0.85, 'y': 1},
    legend_bgcolor = "rgba(0, 0, 0, 0)",
    xaxis = {'tickfont': {'size': 15,
                          'color':'white'},
             'title': {'text':'ALL ROADS',
                       'font': {'size': 20,
                                'color':'white'}},
             'showgrid':True},
    yaxis = {'tickfont': {'size': 15,
                          'color':'white'},
             'title': {'text':'AMOUNT IN (EGP)',
                       'font': {'size': 20,
                                'color':'white'}},
                       'showgrid':True,
                       'tickformat':".3"},
    hoverlabel = {'bgcolor':'orange',
                  'font_size':20,
                  'font_family': 'Times New Roman',
                  'font' : {'color': 'white'}},
    margin = go.layout.Margin( 
              l=0,
              r=0,
              b=0,
              t=0)
                        ) # Margins used to remove all unused spaces
st.plotly_chart(fig1)

# Convert 'Date/Time' column to datetime objects
Updated_Database['Date/Time'] = pd.to_datetime(Updated_Database['Date/Time'])

st.divider()
# Header
st.header("[Cash Flow Projection]", divider = 'red')
# Filter on Trades to get maximum To_Date Profit
st.markdown("#### [*Please select required time frame (From/To):*]", unsafe_allow_html=True)

# Create a Date/Time filter to be applied on cash flow 
t1,t2 = st.columns(2)
# Define Start & Finish Dates
start_date = pd.to_datetime(t1.date_input("Start Date:", value = Updated_Database['Date/Time'].min(), min_value=Updated_Database['Date/Time'].min(),max_value=Updated_Database['Date/Time'].max())) #pd.to_datetime: used to convert variable type to include both date/time to meet below indexing with main database date/time column & Value: Means default value return after rerun & min/max_value: means maximum limited ranges
finish_date = pd.to_datetime(t2.date_input("Finish Date::", value = Updated_Database['Date/Time'].max(), min_value=Updated_Database['Date/Time'].min(),max_value=Updated_Database['Date/Time'].max())) #pd.to_datetime: used to convert variable type to include both date/time to meet below indexing with main database date/time column & Value: Means default value return after rerun & min/max_value: means maximum limited ranges
# Also we used  t1, t2 instead of st to wrote filters in two columns instead two rows

# Filter the data based on the selected date range
filtered_data = Updated_Database[(Updated_Database['Date/Time'] >= start_date) & (Updated_Database['Date/Time'] <= finish_date)]

# Creating a chart showing Cash flow projection
fig2 = go.Figure()

# Add Cash_in trace
fig2.add_trace(go.Scatter(
    x=filtered_data['Date/Time'],
    y=filtered_data['Cash_in(EGP)'],
    mode='lines',
    name='Cash_in(EGP)',
    line=dict(color='green'),
    fill='tozeroy',  # Fill the area below the line
    fillcolor='rgba(0, 255, 0, 0.5)',  # Semi-transparent green
    text=filtered_data['Cash_in(EGP)'],
    textposition='top left'
))

# Add Cash_out trace
fig2.add_trace(go.Scatter(
    x=filtered_data['Date/Time'],
    y=filtered_data['Cash_out(EGP)'],
    mode='lines',
    name='Cash_out(EGP)',
    line=dict(color='red'),
    fill='tozeroy',  # Fill the area below the line
    fillcolor='rgba(255, 0, 0, 0.5)',  # Semi-transparent red
    text=filtered_data['Cash_out(EGP)'],
    textposition='top left'
))

# Show Data Labels & update properties
fig2.update_traces(marker_size=15, textfont={'size': 20, 'color': 'white'})

# Change Figure-02 format
fig2.update_layout(
    plot_bgcolor="rgba(85, 104, 225, 0.15)",
    legend_title={'text': 'Legend',
                  'font': {'size': 15, 'color': 'white'}},
    legend={'font': {'size': 12, 'color': 'white'}, 'x': 0.5, 'y': 1},
    legend_bgcolor="rgba(0, 0, 0, 0)",
    xaxis={'tickfont': {'size': 15, 'color': 'white'},
           'title': {'text': 'Date',
                     'font': {'size': 20, 'color': 'white'}},
           'showgrid': True},
    yaxis={'tickfont': {'size': 15, 'color': 'white'},
           'title': {'text': 'AMOUNT IN (EGP)',
                     'font': {'size': 20, 'color': 'white'}},
           'showgrid': True},
    hoverlabel={'bgcolor': 'orange',
                'font_size': 20,
                'font_family': 'Times New Roman',
                'font': {'color': 'white'}},
    margin=go.layout.Margin(
        l=0,
        r=0,
        b=0,
        t=0)
)

# Show the plot
st.plotly_chart(fig2)

st.divider()
# SubHeader
st.header("Overall Project Segmentation", divider = 'red')
# Filter Selection
st.markdown("#### [*Please Select Categorical & Numerical Attributes:*]", unsafe_allow_html=True)

# Page Division Into 3 columns
c1, c2, c3 = st.columns(3)
with c1:
    # divide each columns into two filters for each chart 
    num_filter1, cat_filter1 = st.columns(2)
    num_filter1 = num_filter1.selectbox('Values:', ['Actual_QTY.','QTY._As _Per_Contract','Qty._Variance','Targeted_Unit_Sale(EGP)','Total_Targeted_Sales(EGP)',
                                                   'Total_Expected_Sales(EGP)','Sales_Variance(EGP)','Actual_Unit_Cost(EGP)','QTY._As _Per_Contract','AC = Actual_Cost_To_Date(EGP)',
                                                   'BAC = Budget @ Completion (EGP)','Progress (%)','EV = Earned Value (EGP)','CPI = Cost Performance index','CV = Cost Variance (EGP)',
                                                   'TCPI = To Complete Performance index','EAC = Estimated @ Completion (EGP)','ETC = Estimate Cost to complete (EGP)',
                                                   'VAC = Variance @ Completion (EGP)','Total_Targeted_Gross_Profit(EGP)','Total_Expected_Gross_Profit(EGP)','Actual_Sales_Progress(EGP)',
                                                   'Actual_To_Date_Profit (EGP)'], key='num_filter1') ## Adding key parameter to each st.select box call to ensure each widget has a unique key for c1, c2, c3.
    cat_filter1 = cat_filter1.selectbox('Legend:', ['Road','Clause','Trade','Brand','Origin','Location'], key='cat_filter1') ## Adding key parameter to each st.select box call to ensure each widget has a unique key for c1, c2, c3.

    # Creating A charts showing total targeted sales per road
    fig3 = px.pie(Updated_Database, values=num_filter1, names=cat_filter1, width = 500, height= 500, hole=0.3)
    # Resize Labels height
    fig3.update_traces(textfont_size=15, textinfo='value+percent', title_position = 'top center', title = num_filter1 + ' for ' + cat_filter1, title_font_size=20, title_font_color='white')
    # Change Figure-03 format
    fig3.update_layout(plot_bgcolor="rgba(85, 104, 225, 0.15)",
                        legend_title= {'text': 'Legend',
                                    'font': {'size': 15,
                                    'color':'white'}},
                        legend= {'font': {'size':12,
                                        'color':'white'}},
                        hoverlabel = {'bgcolor':'orange',
                                    'font_size':20,
                                    'font_family': 'Times New Roman',
                                    'font' : {'color': 'white'}},
                        margin = go.layout.Margin( 
                            l=0,
                            r=0,
                            b=0,
                            t=0)
                            )
    # Plot Figures-03
    st.plotly_chart(fig3)

with c2:
    # divide each columns into two filters for each chart 
    num_filter2, cat_filter2 = st.columns(2)
    num_filter2 = num_filter2.selectbox('Values:', ['Actual_QTY.','QTY._As _Per_Contract','Qty._Variance','Targeted_Unit_Sale(EGP)','Total_Targeted_Sales(EGP)',
                                                   'Total_Expected_Sales(EGP)','Sales_Variance(EGP)','Actual_Unit_Cost(EGP)','QTY._As _Per_Contract','AC = Actual_Cost_To_Date(EGP)',
                                                   'BAC = Budget @ Completion (EGP)','Progress (%)','EV = Earned Value (EGP)','CPI = Cost Performance index','CV = Cost Variance (EGP)',
                                                   'TCPI = To Complete Performance index','EAC = Estimated @ Completion (EGP)','ETC = Estimate Cost to complete (EGP)',
                                                   'VAC = Variance @ Completion (EGP)','Total_Targeted_Gross_Profit(EGP)','Total_Expected_Gross_Profit(EGP)','Actual_Sales_Progress(EGP)',
                                                   'Actual_To_Date_Profit (EGP)'], key='num_filter2') ## Adding key parameter to each st.select box call to ensure each widget has a unique key for c1, c2, c3.
    cat_filter2 = cat_filter2.selectbox('Legend:', ['Clause','Trade','Brand','Origin','Road','Location'], key='cat_filter2') ## Adding key parameter to each st.select box call to ensure each widget has a unique key for c1, c2, c3.

    # Creating A charts showing total targeted sales per road
    fig4 = px.pie(Updated_Database, values=num_filter2, names=cat_filter2, width = 500, height= 500, hole=0.3)
    # Resize Labels height
    fig4.update_traces(textfont_size=15, textinfo='value+percent', title_position = 'top center', title = num_filter2 + ' for ' + cat_filter2, title_font_size=20, title_font_color='white')
    # Change Figure-03 format
    fig4.update_layout(plot_bgcolor="rgba(85, 104, 225, 0.15)",
                        legend_title= {'text': 'Legend',
                                    'font': {'size': 15,
                                    'color':'white'}},
                        legend= {'font': {'size':12,
                                        'color':'white'}},
                        hoverlabel = {'bgcolor':'orange',
                                    'font_size':20,
                                    'font_family': 'Times New Roman',
                                    'font' : {'color': 'white'}},
                        margin = go.layout.Margin( 
                            l=0,
                            r=0,
                            b=0,
                            t=0)
                            )
    # Plot Figures-04
    st.plotly_chart(fig4)

with c3:
    # divide each columns into two filters for each chart 
    num_filter3, cat_filter3 = st.columns(2)
    num_filter3 = num_filter3.selectbox('Values:', ['Actual_QTY.','QTY._As _Per_Contract','Qty._Variance','Targeted_Unit_Sale(EGP)','Total_Targeted_Sales(EGP)',
                                                   'Total_Expected_Sales(EGP)','Sales_Variance(EGP)','Actual_Unit_Cost(EGP)','QTY._As _Per_Contract','AC = Actual_Cost_To_Date(EGP)',
                                                   'BAC = Budget @ Completion (EGP)','Progress (%)','EV = Earned Value (EGP)','CPI = Cost Performance index','CV = Cost Variance (EGP)',
                                                   'TCPI = To Complete Performance index','EAC = Estimated @ Completion (EGP)','ETC = Estimate Cost to complete (EGP)',
                                                   'VAC = Variance @ Completion (EGP)','Total_Targeted_Gross_Profit(EGP)','Total_Expected_Gross_Profit(EGP)','Actual_Sales_Progress(EGP)',
                                                   'Actual_To_Date_Profit (EGP)'], key='num_filter3') ## Adding key parameter to each st.select box call to ensure each widget has a unique key for c1, c2, c3.
    cat_filter3 = cat_filter3.selectbox('Legend:', ['Origin','Clause','Trade','Brand','Road','Location'], key='cat_filter3') ## Adding key parameter to each st.select box call to ensure each widget has a unique key for c1, c2, c3.

    # Creating A charts showing total targeted sales per road
    fig5 = px.pie(Updated_Database, values=num_filter3, names=cat_filter3, width = 500, height= 500, hole=0.3)
    # Resize Labels height
    fig5.update_traces(textfont_size=15, textinfo='value+percent', title_position = 'top center', title = num_filter3 + ' for ' + cat_filter3, title_font_size=20, title_font_color='white')
    # Change Figure-03 format
    fig5.update_layout(plot_bgcolor="rgba(85, 104, 225, 0.15)",
                        legend_title= {'text': 'Legend',
                                    'font': {'size': 15,
                                    'color':'white'}},
                        legend= {'font': {'size':12,
                                        'color':'white'}},
                        hoverlabel = {'bgcolor':'orange',
                                    'font_size':20,
                                    'font_family': 'Times New Roman',
                                    'font' : {'color': 'white'}},
                        margin = go.layout.Margin( 
                            l=0,
                            r=0,
                            b=0,
                            t=0)
                            )
    # Plot Figures-05
    st.plotly_chart(fig5)

st.divider()
# SubHeader
st.header("[Relation Between Trade & Actual Profit (EGP) statistics]", divider = 'red')

# Creating A box chart showing a relation between Trade & Expected Profit (EGP)
fig8 = px.box(Updated_Database, x = "Trade", y = "Actual_To_Date_Profit (EGP)", color="Trade", points="all")
fig8.update_layout(width=1500,height=600)
st.plotly_chart(fig8)

# Filter on Trades to get maximum To_Date Profit
st.markdown("#### [*Please select Trade name to get record of max. gained profit:*]", unsafe_allow_html=True)
Trade_Selection = st.selectbox('', [None, "Electrical System", "Structure Cabling", "TMS", "Network System", "CCTV System", "Light Current System",
            "HVAC System", "Monitoring System", "Video Wall System", "Furniture", "TCS"])
st.markdown("#### [*Max. gained profit through Above Trade is:*]", unsafe_allow_html=True)

# Conditional Filteration based on selected Trade & Max. Profit
# st.write(Updated_Database[(Updated_Database['Trade'] == Trade_Selection) & (Updated_Database['Actual_To_Date_Profit (EGP)'] == Updated_Database['Actual_To_Date_Profit (EGP)'].max())])
st.write(Updated_Database[Updated_Database['Actual_To_Date_Profit (EGP)'] == Updated_Database[Updated_Database['Trade']==Trade_Selection]['Actual_To_Date_Profit (EGP)'].max()])

st.divider()
# SubHeader
st.header("[Relation Between Clauses & Actual Profit (EGP) statistics]", divider = 'red')
# Creating A box chart showing a relation between Trade & Expected Profit (EGP)
fig8 = px.box(Updated_Database, x = "Clause", y = "Actual_To_Date_Profit (EGP)", color="Clause", points="all")
fig8.update_layout(width=1500,height=600)
st.plotly_chart(fig8)

# Filter on Trades to get maximum To_Date Profit
st.markdown("#### [*Please select clause name to get record of max. gained profit:*]", unsafe_allow_html=True)
Clause_Selection = st.selectbox('', [None, "PWR Cables", "1st Fix devices", "3rd Fix devices", "PWR Cable Trays", "Data Cable Trays", "Elec. Panels", "Raceways", "Earthing",
             "Gen. Set", "TMS", "IP telephones", "Network", "Data Racks", "Data cables", "CCTV", "Fire Alarm",
             "Fire Fighting", "Access Control", "HVAC", "Work Station", "Video Wall", "Furniture", "UPS", "Structure Cabling", 
             "EMT Devices", "Infrastructure", "TCS"])
st.markdown("#### [*Max. gained profit Was through Above Clause is:*]", unsafe_allow_html=True)

# Conditional Filteration based on selected Trade & Max. Profit
# st.write(Updated_Database[(Updated_Database['Trade'] == Trade_Selection) & (Updated_Database['Actual_To_Date_Profit (EGP)'] == Updated_Database['Actual_To_Date_Profit (EGP)'].max())])
st.write(Updated_Database[Updated_Database['Actual_To_Date_Profit (EGP)'] == Updated_Database[Updated_Database['Clause']==Clause_Selection]['Actual_To_Date_Profit (EGP)'].max()])

st.divider()
# SubHeader
st.header("[Actual Sales VS Actual Profit (%) Per Road]", divider = 'red')

# Creating A chart showing a relation between EV, AC, CV per road
fig9 = px.histogram(Updated_Database, x='Road', y=["Actual_Sales_Progress(EGP)","Actual_To_Date_Profit (EGP)"], height=500, width=1500, color_discrete_sequence=['seagreen','mediumvioletred'], text_auto=True, barmode="stack", barnorm= "percent")

# Show Data Labels & update properties
fig9.update_traces(textfont_size=40, textangle=0, textposition="auto", textfont_color= "white", texttemplate='%{y:.1f}%', hovertemplate='%{y:.1f}%') #This will tell plotly that you want the display of y values in the format .2f meaning 2 decimal places after the decimal point

# Change Figure-09 format
fig9.update_layout(
    plot_bgcolor="rgba(85, 104, 225, 0.15)",
    legend_title= {'text': 'Legend',
                   'font': {'size': 15,
                            'color':'white'}},
    legend= {'font': {'size':12,
                      'color':'white'},
                      'x':1.05, 'y': 1},
    legend_bgcolor = "rgba(0, 0, 0, 0)",
    xaxis = {'tickfont': {'size': 15,
                          'color':'white'},
             'title': {'text':'ALL ROADS',
                       'font': {'size': 20,
                                'color':'white'}},
             'showgrid':True},
    yaxis = {'tickfont': {'size': 15,
                          'color':'white'},
             'title': {'text':'Actual Sales & Actual Profit IN (EGP)',
                       'font': {'size': 20,
                                'color':'white'}},
                       'showgrid':True},
    hoverlabel = {'bgcolor':'orange',
                  'font_size':20,
                  'font_family': 'Times New Roman',
                  'font' : {'color': 'white'}},
    margin = go.layout.Margin( 
              l=0,
              r=0,
              b=0,
              t=0,
              pad=0)
                        ) # Margins used to remove all unused spaces
st.plotly_chart(fig9)

st.divider()
# SubHeader
st.header("Relation Between Numerical Values (Optional)", divider = 'red')

# Adding FIlters Assigned for Scatter Plot
st.markdown("#### [*Please select Numerical Attribute for X-axis, Y-axis and legend:*]", unsafe_allow_html=True)
f1,f2,f3,f4 = st.columns(4)
x_axis_num_filter = f1.selectbox('X_axis_Value:', ['Actual_QTY.','QTY._As _Per_Contract','Qty._Variance','Targeted_Unit_Sale(EGP)','Total_Targeted_Sales(EGP)',
                                                   'Total_Expected_Sales(EGP)','Sales_Variance(EGP)','Actual_Unit_Cost(EGP)','QTY._As _Per_Contract','AC = Actual_Cost_To_Date(EGP)',
                                                   'BAC = Budget @ Completion (EGP)','Progress (%)','EV = Earned Value (EGP)','CPI = Cost Performance index','CV = Cost Variance (EGP)',
                                                   'TCPI = To Complete Performance index','EAC = Estimated @ Completion (EGP)','ETC = Estimate Cost to complete (EGP)',
                                                   'VAC = Variance @ Completion (EGP)','Total_Targeted_Gross_Profit(EGP)','Total_Expected_Gross_Profit(EGP)','Actual_Sales_Progress(EGP)',
                                                   'Actual_To_Date_Profit (EGP)'])
y_axis_num_filter = f2.selectbox('Y_axis_Value:', ['Actual_QTY.','QTY._As _Per_Contract','Qty._Variance','Targeted_Unit_Sale(EGP)','Total_Targeted_Sales(EGP)',
                                                   'Total_Expected_Sales(EGP)','Sales_Variance(EGP)','Actual_Unit_Cost(EGP)','QTY._As _Per_Contract','AC = Actual_Cost_To_Date(EGP)',
                                                   'BAC = Budget @ Completion (EGP)','Progress (%)','EV = Earned Value (EGP)','CPI = Cost Performance index','CV = Cost Variance (EGP)',
                                                   'TCPI = To Complete Performance index','EAC = Estimated @ Completion (EGP)','ETC = Estimate Cost to complete (EGP)',
                                                   'VAC = Variance @ Completion (EGP)','Total_Targeted_Gross_Profit(EGP)','Total_Expected_Gross_Profit(EGP)','Actual_Sales_Progress(EGP)',
                                                   'Actual_To_Date_Profit (EGP)'])
num_filter = f3.selectbox('Numerical Filtering:', ['Actual_QTY.','QTY._As _Per_Contract','Qty._Variance','Targeted_Unit_Sale(EGP)','Total_Targeted_Sales(EGP)',
                                                   'Total_Expected_Sales(EGP)','Sales_Variance(EGP)','Actual_Unit_Cost(EGP)','QTY._As _Per_Contract','AC = Actual_Cost_To_Date(EGP)',
                                                   'BAC = Budget @ Completion (EGP)','Progress (%)','EV = Earned Value (EGP)','CPI = Cost Performance index','CV = Cost Variance (EGP)',
                                                   'TCPI = To Complete Performance index','EAC = Estimated @ Completion (EGP)','ETC = Estimate Cost to complete (EGP)',
                                                   'VAC = Variance @ Completion (EGP)','Total_Targeted_Gross_Profit(EGP)','Total_Expected_Gross_Profit(EGP)','Actual_Sales_Progress(EGP)',
                                                   'Actual_To_Date_Profit (EGP)'])
cat_filter2 = f4.selectbox('Categorical Filtering:', ['Clause','Trade','Brand','Origin','Road','Location'])

# Creating A scatter plot showing relation between numerical Values 
fig6 = px.scatter(Updated_Database, x = x_axis_num_filter, y = y_axis_num_filter, color = cat_filter2, height=500, width=1500)
sns.regplot(data = Updated_Database, x = x_axis_num_filter, y = y_axis_num_filter)
plt.show()

# Change Figure-06 format
fig6.update_layout(
    plot_bgcolor="rgba(85, 104, 225, 0.15)",
    title = {'text': 'Relation between ' + x_axis_num_filter + ' & ' + y_axis_num_filter,
             'y':0.95,
             'x':0.5,
             'font_size': 25,
             'xanchor': 'center',
             'yanchor': 'top'},
    legend_title= {'text': 'Legend',
                   'font': {'size': 15,
                   'color':'white'}},
    legend= {'font': {'size':12,
                      'color':'white'},
                      'x':0.9, 'y':0},
    legend_bgcolor = "rgba(0, 0, 0, 0)",
    hoverlabel = {'bgcolor':'orange',
                  'font_size':20,
                  'font_family': 'Times New Roman',
                  'font' : {'color': 'white'}},
    xaxis = {'tickfont': {'size': 15,
                          'color':'white'},
             'title': {'text':x_axis_num_filter,
                       'font': {'size': 20,
                                'color':'white'}},
             'showgrid':True},
    yaxis = {'tickfont': {'size': 15,
                          'color':'white'},
             'title': {'text':y_axis_num_filter,
                       'font': {'size': 20,
                                'color':'white'}},
                       'showgrid':True},
    margin = go.layout.Margin( 
              l=0,
              r=0,
              b=0,
              t=0)
                    )
# Plot Figures-06
st.plotly_chart(fig6) 

st.divider()
# SubHeader
st.header("Materials Variation List:", divider = 'red')
variation_button = st.button("List of Variances")
if variation_button:
    st.write(Updated_Database[Updated_Database['Qty._Variance']>0].reset_index())

# Signature
st.sidebar.markdown("## :grey Designed & Created by: Eng.[Ashraf Mahdy Elshaer](https://www.linkedin.com/in/ashraf-elshaer-6261b268/)", unsafe_allow_html=True)
st.sidebar.divider()
# st.sidebar.markdown("## :grey Supervised by: Eng.Omar Hanafy", unsafe_allow_html=True)
# st.sidebar.divider()
# st.sidebar.markdown("## :grey Approved by: Eng.Mahmoud Abdelsamee", unsafe_allow_html=True)
