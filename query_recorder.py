import streamlit as st
import pandas as pd
from datetime import datetime
import os

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
    st.session_state.data.at[index, 'Date'] = date
    st.session_state.data.at[index, 'Client'] = client
    st.session_state.data.at[index, 'AM'] = am
    st.session_state.data.at[index, 'SF Ticket'] = sf
    st.session_state.data.at[index, 'Use Case'] = use_case
    st.session_state.data.at[index, 'Notes'] = notes
    st.session_state.data.at[index, 'Code'] = code
    save_data(st.session_state.data)  # Save data to CSV

# Function to delete an entry
def delete_entry(index):
    st.session_state.data = st.session_state.data.drop(index).reset_index(drop=True)
    save_data(st.session_state.data)  # Save data to CSV

# Display the table
def display_table(data):
    st.write(data)

display_table(st.session_state.data)

# Edit/delete section at the end
st.header("Edit/Delete Entries")

# Allow user to select entry to edit or delete
index = st.selectbox("Select an entry by index:", options=list(st.session_state.data.index), format_func=lambda x: f"Entry {x}")

if index is not None and index in st.session_state.data.index:
    entry = st.session_state.data.iloc[index]
    
    # Display the selected entry for editing
    st.subheader(f"Edit Entry {index}")
    date_input = st.date_input("Date", pd.to_datetime(entry['Date']).date())
    client_input = st.text_input("Client", entry['Client'])
    am_input = st.text_input("AM", entry['AM'])
    ticket_input = st.text_input("SF Ticket", entry['SF Ticket'])
    use_case_input = st.text_input("Use Case", entry['Use Case'])
    notes_input = st.text_area("Notes", entry['Notes'])
    code_input = st.text_area("Code", entry['Code'], height=200)
    
    if st.button("Update Entry"):
        update_entry(index, date_input.strftime('%Y-%m-%d'), client_input, am_input, ticket_input, use_case_input, notes_input, code_input)
        st.success("Entry updated!")
        st.experimental_rerun()  # Refresh the page to update the table
    
    if st.button("Delete Entry"):
        delete_entry(index)
        st.success("Entry deleted!")
        st.experimental_rerun()  # Refresh the page to update the table

# User input section for adding new entries
if 'edit_mode' not in st.session_state or not st.session_state.edit_mode:
    st.header("Add New Entry")
    
    # Set default values only if not present in session state
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
