import streamlit as st
import pandas as pd
from datetime import datetime
import json
import gspread
from google.oauth2 import service_account

st.set_page_config(layout="wide")
st.title("Query Database")

# Function to load data from Google Sheets
def load_data_from_google_sheets():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )

    client = gspread.authorize(credentials)
    sheet_id = st.secrets["sheet_id"]
    sheet = client.open_by_key(sheet_id)
    worksheet = sheet.worksheet("Sheet1")
    data = worksheet.get_all_values()
    headers = data.pop(0)
    df = pd.DataFrame(data, columns=headers)
    return df

# Function to save data to Google Sheets
def save_data_to_google_sheets(data):
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )

    client = gspread.authorize(credentials)
    sheet_id = st.secrets["sheet_id"]
    sheet = client.open_by_key(sheet_id)
    worksheet = sheet.worksheet("Sheet1")
    
    # Clear the existing content
    worksheet.clear()

    # Update with new data
    worksheet.update([data.columns.values.tolist()] + data.values.tolist())
    st.write(f"Data saved to Google Sheets with ID {sheet_id}")

# Initialize session state for the table and input fields
if 'data' not in st.session_state:
    st.session_state.data = load_data_from_google_sheets()

# Function to add a new entry
def add_entry(date, client, am, sf, use_case, notes, code, report_id):
    if code:
        try:
            formatted_code = json.dumps(json.loads(code), indent=4)
        except json.JSONDecodeError:
            st.error("Invalid JSON format in the Code field.")
            return
    else:
        formatted_code = ""

    new_entry = pd.DataFrame({
        'Date': [date], 
        'Client': [client],
        'AM': [am],
        'SF Ticket': [sf],
        'Use Case': [use_case],
        'Notes': [notes],
        'Code': [formatted_code],
        'Report ID': [report_id]
    })
    st.session_state.data = pd.concat([st.session_state.data, new_entry], ignore_index=True)
    
    # Save data to Google Sheets
    save_data_to_google_sheets(st.session_state.data)
    
# Function to update an existing entry
def update_entry(index, date, client, am, sf, use_case, notes, code, report_id):
    if code:
        try:
            formatted_code = json.dumps(json.loads(code), indent=4)
        except json.JSONDecodeError:
            st.error("Invalid JSON format in the Code field.")
            return
    else:
        formatted_code = ""

    st.session_state.data.at[index, 'Date'] = date
    st.session_state.data.at[index, 'Client'] = client
    st.session_state.data.at[index, 'AM'] = am
    st.session_state.data.at[index, 'SF Ticket'] = sf
    st.session_state.data.at[index, 'Use Case'] = use_case
    st.session_state.data.at[index, 'Notes'] = notes
    st.session_state.data.at[index, 'Code'] = formatted_code
    st.session_state.data.at[index, 'Report ID'] = report_id
    
    # Save data to Google Sheets
    save_data_to_google_sheets(st.session_state.data)

# Function to delete an entry
def delete_entry(index):
    st.session_state.data = st.session_state.data.drop(index).reset_index(drop=True)
    
    # Save data to Google Sheets
    save_data_to_google_sheets(st.session_state.data)

# Display the table with entries and Edit/Delete buttons
def display_table(data):
    st.write("### Current Entries")
    edited_data = data.copy()

    for index, row in edited_data.iterrows():
        with st.expander(f"Entry {index} - {row['Client']}"):
            row_col1, row_col2, row_col3, row_col4, row_col5, row_col6, row_col7, row_col8, row_col9, row_col10 = st.columns([1, 2, 2, 2, 2, 2, 2, 2, 2, 2])
            
            row_col1.write(index)
            row_col2.write(row['Date'])
            row_col3.write(row['Client'])
            row_col4.write(row['AM'])
            row_col5.write(row['SF Ticket'])
            row_col6.write(row['Use Case'])
            row_col7.write(row['Notes'][:20] + '...' if len(row['Notes']) > 20 else row['Notes'])
            row_col8.write(row['Code'][:20] + '...' if len(row['Code']) > 20 else row['Code'])
            row_col9.write(row['Report ID'])
            
            if row_col10.button("Edit", key=f"edit_{index}"):
                st.session_state.edit_index = index
                st.session_state.edit_mode = True
            if row_col10.button("Delete", key=f"delete_{index}"):
                delete_entry(index)
                st.success(f"Entry {index} deleted!")
                st.experimental_rerun()

    if 'edit_mode' in st.session_state and st.session_state.edit_mode:
        index = st.session_state.edit_index
        entry = data.iloc[index]
        
        st.write(f"### Editing Entry {index}")
        
        # Display the edit form
        date_input = st.date_input("Date", pd.to_datetime(entry['Date']), key=f"edit_date_{index}")
        client_input = st.text_input("Client", entry['Client'], key=f"edit_client_{index}")
        am_input = st.text_input("AM", entry['AM'], key=f"edit_am_{index}")
        ticket_input = st.text_input("SF Ticket", entry['SF Ticket'], key=f"edit_ticket_{index}")
        use_case_input = st.text_input("Use Case", entry['Use Case'], key=f"edit_use_case_{index}")
        notes_input = st.text_area("Notes", entry['Notes'], key=f"edit_notes_{index}")
        code_input = st.text_area("Code", entry['Code'], key=f"edit_code_{index}", height=200)
        report_input = st.text_input("Report ID", entry['Report ID'], key=f"edit_report_{index}")
        
        if st.button("Update Entry", key=f"update_{index}"):
            update_entry(index, date_input.strftime('%Y-%m-%d'), client_input, am_input, ticket_input, use_case_input, notes_input, code_input, report_input)
            st.success("Entry updated!")
            st.session_state.edit_mode = False
            st.experimental_rerun()

# Display the table with entries
st.header("Current Entries")
display_table(st.session_state.data)

# Expandable section for adding new entries
with st.expander("Add New Entry"):
    st.markdown("## Add a New Entry")
    st.write("Fill in the details below to add a new entry to the database.")
    
    date_input = st.date_input("**Date**", datetime.today().date())
    client_input = st.text_input("**Client**")
    am_input = st.text_input("**AM**")
    ticket_input = st.text_input("**SF Ticket**")
    use_case_input = st.text_input("**Use Case**")
    notes_input = st.text_area("**Notes**", height=100)
    code_input = st.text_area("**Code**", height=200)
    report_input = st.text_input("**Report ID**")

    if st.button("Add Entry"):
        st.balloons()
        add_entry(
            date_input.strftime('%Y-%m-%d'), 
            client_input, 
            am_input, 
            ticket_input, 
            use_case_input, 
            notes_input, 
            code_input, 
            report_input
        )
        st.success("Entry added!")
        st.experimental_rerun()

# Option to upload data from a CSV file
st.header("Upload Data from CSV")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file, parse_dates=['Date'])
    data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')  # Format the date
    st.session_state.data = pd.concat([st.session_state.data, data], ignore_index=True)
    save_data_to_google_sheets(st.session_state.data)
    st.success("Data loaded from CSV.")
