import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json

st.set_page_config(layout="wide")
st.title("Query Database")

# Define the CSV and text file paths
CSV_FILE_PATH = 'data.csv'
TEXT_FILE_PATH = 'entries.txt'

# Function to load data from the default CSV file if it exists
def load_data():
    if os.path.isfile(CSV_FILE_PATH):
        data = pd.read_csv(CSV_FILE_PATH, parse_dates=['Date'])
        data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')  # Format the date
        return data
    else:
        return pd.DataFrame(columns=['Date', 'Client', 'AM', 'SF Ticket', 'Use Case', 'Notes', 'Code', 'Report ID'])

# Save data to CSV file
def save_data(data):
    data.to_csv(CSV_FILE_PATH, index=False)
    st.write(f"Data saved to {CSV_FILE_PATH}")

# Append entry to text file
def append_to_text_file(entry):
    with open(TEXT_FILE_PATH, 'a') as f:
        f.write(f"{entry}\n")
    st.write(f"Entry appended to {TEXT_FILE_PATH}")

# Initialize session state for the table and input fields
if 'data' not in st.session_state:
    st.session_state.data = load_data()

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
    save_data(st.session_state.data)  # Save data to CSV
    
    # Append to text file
    entry_dict = new_entry.to_dict('records')[0]
    append_to_text_file(entry_dict)

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
    save_data(st.session_state.data)  # Save data to CSV

# Function to delete multiple entries
def delete_entries(indices):
    st.session_state.data = st.session_state.data.drop(indices).reset_index(drop=True)
    save_data(st.session_state.data)  # Save data to CSV

# Display the table with entries
def display_table(data):
    # Format the Code column for better display
    data['Code'] = data['Code'].apply(lambda x: json.dumps(json.loads(x), indent=4) if x else x)
    st.dataframe(data)

# Display the table with entries
st.header("Current Entries")
display_table(st.session_state.data)

# Expandable section for adding new entries
with st.expander("Add New Entry"):
    st.markdown("### Fill in the details below to add a new entry:")
    
    # Columns for input fields to make it more organized
    col1, col2 = st.columns(2)
    
    with col1:
        date_input = st.date_input("Date", datetime.today().date())
        client_input = st.text_input("Client")
        am_input = st.text_input("AM")
        ticket_input = st.text_input("SF Ticket")
    
    with col2:
        use_case_input = st.text_input("Use Case")
        notes_input = st.text_area("Notes")
        code_input = st.text_area("Code", height=200)
        report_input = st.text_input("Report ID")

    if st.button("Add Entry"):
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
        # Clear input fields by resetting session state values
        st.session_state.date_input = datetime.today().date()
        st.session_state.client_input = ""
        st.session_state.am_input = ""
        st.session_state.ticket_input = ""
        st.session_state.use_case_input = ""
        st.session_state.notes_input = ""
        st.session_state.code_input = ""
        st.session_state.report_input = ""
        st.experimental_rerun()
        
    date_input = st.date_input("Date", st.session_state.date_input)
    client_input = st.text_input("Client", st.session_state.client_input)
    am_input = st.text_input("AM", st.session_state.am_input)
    ticket_input = st.text_input("SF Ticket", st.session_state.ticket_input)
    use_case_input = st.text_input("Use Case", st.session_state.use_case_input)
    notes_input = st.text_area("Notes", st.session_state.notes_input)
    code_input = st.text_area("Code", st.session_state.code_input, height=200)
    report_input = st.text_input("Report ID", st.session_state.report_input)

    if st.button("Add Entry"):
        add_entry(date_input.strftime('%Y-%m-%d'), client_input, am_input, ticket_input, use_case_input, notes_input, code_input, report_input)
        st.success("Entry added!")
        # Clear input fields by resetting session state values
        st.session_state.date_input = datetime.today().date()
        st.session_state.client_input = ""
        st.session_state.am_input = ""
        st.session_state.ticket_input = ""
        st.session_state.use_case_input = ""
        st.session_state.notes_input = ""
        st.session_state.code_input = ""
        st.session_state.report_input = ""
        st.experimental_rerun()

# Edit/Delete section at the end
st.header("Edit/Delete Entries")

# Allow user to select entries to edit or delete
options = [f"{i} - {row['Client']}/{row['AM']}" for i, row in st.session_state.data.iterrows()]
selected_indices = st.multiselect("Select entries to edit/delete:", options=options)

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
    save_data(st.session_state.data)
    st.success("Data loaded from CSV.")
