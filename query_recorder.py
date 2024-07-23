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

# Function to load data from an uploaded CSV file
def load_data_from_csv(uploaded_file):
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file, parse_dates=['Date'])
        data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')  # Format the date
        st.session_state.data = data
        st.success("Data loaded from CSV.")
    else:
        st.warning("No file uploaded. Initializing empty DataFrame.")
        st.session_state.data = pd.DataFrame(columns=['Date', 'Client', 'AM', 'SF Ticket', 'Use Case', 'Notes', 'Code', 'Report ID'])

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

    if 'Date' in st.session_state.data.columns:
        st.session_state.data.at[index, 'Date'] = date
    if 'Client' in st.session_state.data.columns:
        st.session_state.data.at[index, 'Client'] = client
    if 'AM' in st.session_state.data.columns:
        st.session_state.data.at[index, 'AM'] = am
    if 'SF Ticket' in st.session_state.data.columns:
        st.session_state.data.at[index, 'SF Ticket'] = sf
    if 'Use Case' in st.session_state.data.columns:
        st.session_state.data.at[index, 'Use Case'] = use_case
    if 'Notes' in st.session_state.data.columns:
        st.session_state.data.at[index, 'Notes'] = notes
    if 'Code' in st.session_state.data.columns:
        st.session_state.data.at[index, 'Code'] = formatted_code
    if 'Report ID' in st.session_state.data.columns:
        st.session_state.data.at[index, 'Report ID'] = report_id
    save_data(st.session_state.data)  # Save data to CSV

# Function to delete an entry
def delete_entry(index):
    st.session_state.data = st.session_state.data.drop(index).reset_index(drop=True)
    save_data(st.session_state.data)  # Save data to CSV

# Display the table with entries
def display_table(data):
    # Format the Code column for better display
    data['Code'] = data['Code'].apply(lambda x: json.dumps(json.loads(x), indent=4) if x else x)
    st.dataframe(data)

# Code preview with expand/collapse option
def display_code_preview(code_text):
    preview_length = 200  # Number of characters to show in preview
    if len(code_text) > preview_length:
        st.text_area("Code Preview", code_text[:preview_length] + '...', height=100, max_chars=None)
        if st.button("Show More"):
            st.code(code_text, language='json')
    else:
        st.code(code_text, language='json')

# Display the table with entries
st.header("Current Entries")
display_table(st.session_state.data)


# User input section for adding new entries
st.header("Add New Entry")
if 'date_input' not in st.session_state:
    st.session_state.date_input = datetime.today().date()
if 'client_input' not in st.session_state:
    st.session_state.client_input = ""
if 'am_input' not in st.session_state:
    st.session_state.am_input = ""
if 'ticket_input' not in st.session_state:
    st.session_state.ticket_input = ""
if 'use_case_input' not in st.session_state:
    st.session_state.use_case_input = ""
if 'notes_input' not in st.session_state:
    st.session_state.notes_input = ""
if 'code_input' not in st.session_state:
    st.session_state.code_input = ""
if 'report_input' not in st.session_state:
    st.session_state.report_input = ""

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

# Edit/Delete section at the end
st.header("Edit/Delete Entries")

# Allow user to select entry to edit or delete
options = [f"{i} - {row['Client']}/{row['AM']}" for i, row in st.session_state.data.iterrows()]
index = st.selectbox("Select an entry to edit/delete:", options=[None] + options)

if index:
    idx = int(index.split(" - ")[0])
    st.subheader(f"Editing Entry {idx}")
    entry = st.session_state.data.iloc[idx]

    # Display the edit form only if an entry is selected
    if 'Date' in entry:
        date_input = st.date_input("Date", pd.to_datetime(entry['Date']), key=f"edit_date_{idx}")
    if 'Client' in entry:
        client_input = st.text_input("Client", entry['Client'], key=f"edit_client_{idx}")
    if 'AM' in entry:
        am_input = st.text_input("AM", entry['AM'], key=f"edit_am_{idx}")
    if 'SF Ticket' in entry:
        ticket_input = st.text_input("SF Ticket", entry['SF Ticket'], key=f"edit_ticket_{idx}")
    if 'Use Case' in entry:
        use_case_input = st.text_input("Use Case", entry['Use Case'], key=f"edit_use_case_{idx}")
    if 'Notes' in entry:
        notes_input = st.text_area("Notes", entry['Notes'], key=f"edit_notes_{idx}")
    if 'Code' in entry:
        code_input = st.text_area("Code", entry['Code'], key=f"edit_code_{idx}", height=200)
    if 'Report ID' in entry:
        report_input = st.text_input("Report ID", entry['Report ID'], key=f"edit_report_{idx}")
    # Option to upload data from a CSV file
    
    st.header("Upload Data from CSV")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
    load_data_from_csv(uploaded_file)

    if st.button("Update Entry"):
        update_entry(idx, date_input.strftime('%Y-%m-%d'), client_input, am_input, ticket_input, use_case_input, notes_input, code_input, report_input)
        st.success("Entry updated!")
        st.experimental_rerun()  # Refresh the page to update the table

    if st.button("Delete Entry"):
        delete_entry(idx)
        st.success("Entry deleted!")
        st.experimental_rerun()  # Refresh the page to update the table
