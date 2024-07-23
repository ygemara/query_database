import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(layout= "wide")
st.title("Query Database")

# Define the CSV and text file paths
CSV_FILE_PATH = 'data.csv'
TEXT_FILE_PATH = 'entries.txt'

# Load data from CSV file if it exists
def load_data():
    if os.path.isfile(CSV_FILE_PATH):
        data = pd.read_csv(CSV_FILE_PATH, parse_dates=['Date'])
        data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')  # Format the date
        return data
    else:
        return pd.DataFrame(columns=['Date', 'Client', 'AM', 'SF Ticket', 'Use Case', 'Notes', 'Code'])

# Save data to CSV file
def save_data(data):
    data.to_csv(CSV_FILE_PATH, index=False)

# Append entry to text file
def append_to_text_file(entry):
    with open(TEXT_FILE_PATH, 'a') as f:
        f.write(f"{entry}\n")

# Initialize session state for the table and input fields
if 'data' not in st.session_state:
    st.session_state.data = load_data()
    save_data(st.session_state.data)  # Save data to CSV to ensure consistency

# Function to add a new entry
def add_entry(date, client, am, sf, use_case, notes, code):
    new_entry = pd.DataFrame({
        'Date': [date], 
        'Client': [client],
        'AM': [am],
        'SF Ticket': [sf],
        'Use Case': [use_case],
        'Notes': [notes],
        'Code': [code]
    })
    st.session_state.data = pd.concat([st.session_state.data, new_entry], ignore_index=True)
    save_data(st.session_state.data)  # Save data to CSV
    
    # Append to text file
    append_to_text_file(new_entry.to_dict('records')[0])

# Function to update an existing entry
def update_entry(index, date, client, am, sf, use_case, notes, code):
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
        st.session_state.data.at[index, 'Code'] = code
    save_data(st.session_state.data)  # Save data to CSV

# Function to delete an entry
def delete_entry(index):
    st.session_state.data = st.session_state.data.drop(index).reset_index(drop=True)
    save_data(st.session_state.data)  # Save data to CSV

# Display the table with entries
def display_table(data):
    st.write(data)

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

date_input = st.date_input("Date", st.session_state.date_input)
client_input = st.text_input("Client", st.session_state.client_input)
am_input = st.text_input("AM", st.session_state.am_input)
ticket_input = st.text_input("SF Ticket", st.session_state.ticket_input)
use_case_input = st.text_input("Use Case", st.session_state.use_case_input)
notes_input = st.text_area("Notes", st.session_state.notes_input)
code_input = st.text_area("Code", st.session_state.code_input, height=200)

if st.button("Add Entry"):
    add_entry(date_input.strftime('%Y-%m-%d'), client_input, am_input, ticket_input, use_case_input, notes_input, code_input)
    st.success("Entry added!")
    # Clear input fields by resetting session state values
    st.session_state.date_input = datetime.today().date()
    st.session_state.client_input = ""
    st.session_state.am_input = ""
    st.session_state.ticket_input = ""
    st.session_state.use_case_input = ""
    st.session_state.notes_input = ""
    st.session_state.code_input = ""

# Edit/Delete section at the end
st.header("Edit/Delete Entries")

# Allow user to select entry to edit or delete
index = st.selectbox("Select an entry to edit/delete by index:", options=[None] + list(st.session_state.data.index))

if index is not None and index >= 0 and len(st.session_state.data) > 0:
    st.subheader(f"Editing Entry {index}")
    entry = st.session_state.data.iloc[index]

    # Display the edit form only if an entry is selected
    if 'Date' in entry:
        date_input = st.date_input("Date", pd.to_datetime(entry['Date']), key=f"edit_date_{index}")
    if 'Client' in entry:
        client_input = st.text_input("Client", entry['Client'], key=f"edit_client_{index}")
    if 'AM' in entry:
        am_input = st.text_input("AM", entry['AM'], key=f"edit_am_{index}")
    if 'SF Ticket' in entry:
        ticket_input = st.text_input("SF Ticket", entry['SF Ticket'], key=f"edit_ticket_{index}")
    if 'Use Case' in entry:
        use_case_input = st.text_input("Use Case", entry['Use Case'], key=f"edit_use_case_{index}")
    if 'Notes' in entry:
        notes_input = st.text_area("Notes", entry['Notes'], key=f"edit_notes_{index}")
    if 'Code' in entry:
        code_input = st.text_area("Code", entry['Code'], key=f"edit_code_{index}", height=200)

    if st.button("Update Entry"):
        update_entry(index, date_input.strftime('%Y-%m-%d'), client_input, am_input, ticket_input, use_case_input, notes_input, code_input)
        st.success("Entry updated!")
        st.experimental_rerun()  # Refresh the page to update the table

    if st.button("Delete Entry"):
        delete_entry(index)
        st.success("Entry deleted!")
        st.experimental_rerun()  # Refresh the page to update the table
