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
    df = pd.DataFrame(data, columns=headers).sort_values("Date",ascending = False)
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

# Function to delete multiple entries
def delete_entries(indices):
    st.session_state.data = st.session_state.data.drop(indices).reset_index(drop=True)
    
    # Save data to Google Sheets
    save_data_to_google_sheets(st.session_state.data)

# Display the table with entries
def display_table(data):
    def format_code(x):
        if x:
            try:
                return json.dumps(json.loads(x), indent=4)
            except json.JSONDecodeError:
                return x  # Return the original value if it's not valid JSON
        return x

    data['Code'] = data['Code'].apply(format_code)
    st.dataframe(data)

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
        st.snow()
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

# Edit/Delete section at the end
st.header("Edit/Delete Entries")

# Allow user to select entries to edit or delete
options = [f"{i} - {row['Client']}/{row['AM']}" for i, row in st.session_state.data.iterrows()]
selected_indices = st.multiselect("Select entries to edit/delete:", options)

if selected_indices:
    idx_list = [int(i.split(" - ")[0]) for i in selected_indices]
    if len(idx_list) == 1:
        idx = idx_list[0]
        st.subheader(f"Editing Entry {idx}")
        entry = st.session_state.data.iloc[idx]

        # Display the edit form only if an entry is selected
        date_input = st.date_input("Date", pd.to_datetime(entry['Date']), key=f"edit_date_{idx}")
        client_input = st.text_input("Client", entry['Client'], key=f"edit_client_{idx}")
        am_input = st.text_input("AM", entry['AM'], key=f"edit_am_{idx}")
        ticket_input = st.text_input("SF Ticket", entry['SF Ticket'], key=f"edit_ticket_{idx}")
        use_case_input = st.text_input("Use Case", entry['Use Case'], key=f"edit_use_case_{idx}")
        notes_input = st.text_area("Notes", entry['Notes'], key=f"edit_notes_{idx}")
        code_input = st.text_area("Code", entry['Code'], key=f"edit_code_{idx}", height=200)
        report_input = st.text_input("Report ID", entry['Report ID'], key=f"edit_report_{idx}")

        if st.button("Update Entry"):
            st.snow()
            update_entry(idx, date_input.strftime('%Y-%m-%d'), client_input, am_input, ticket_input, use_case_input, notes_input, code_input, report_input)
            st.success("Entry updated!")
            st.experimental_rerun()  # Refresh the page to update the table

    if st.button("Delete Selected Entries"):
        delete_entries(idx_list)
        st.success("Selected entries deleted!")
        st.experimental_rerun()  # Refresh the page to update the table

# Option to upload data from a CSV file
st.header("Upload Data from CSV")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file, parse_dates=['Date'])
    data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')  # Format the date
    st.session_state.data = pd.concat([st.session_state.data, data], ignore_index=True)
    save_data_to_google_sheets(st.session_state.data)
    st.success("Data loaded from CSV.")
