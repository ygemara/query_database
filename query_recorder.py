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
        return pd.DataFrame(columns=['Date', 'Client', 'AM', 'Use Case', 'Notes', 'Code'])

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
def add_entry(date, client, am, use_case, notes, code):
    new_entry = pd.DataFrame({
        'Date': [date], 
        'Client': [client],
        'AM': [am],
        'Use Case': [use_case],
        'Notes': [notes],
        'Code': [code]
    })
    st.session_state.data = pd.concat([st.session_state.data, new_entry], ignore_index=True)
    save_data(st.session_state.data)  # Save data to CSV
    
    # Append to text file
    append_to_text_file(new_entry.to_dict('records')[0])

# Function to update an existing entry
def update_entry(index, date, client, am, use_case, notes, code):
    st.session_state.data.at[index, 'Date'] = date
    st.session_state.data.at[index, 'Client'] = client
    st.session_state.data.at[index, 'AM'] = am
    st.session_state.data.at[index, 'Use Case'] = use_case
    st.session_state.data.at[index, 'Notes'] = notes
    st.session_state.data.at[index, 'Code'] = code
    save_data(st.session_state.data)  # Save data to CSV

# Function to delete an entry
def delete_entry(index):
    st.session_state.data = st.session_state.data.drop(index).reset_index(drop=True)
    save_data(st.session_state.data)  # Save data to CSV

# Display the table with expandable "Code" column and edit/delete options
def display_expandable_table(data):
    expanded_row = st.session_state.get('expanded_row', None)
    for idx, row in data.iterrows():
        cols = st.columns(len(row) + 2)
        for i, (col, value) in enumerate(row.items()):
            if i == len(row) - 1:  # Last column (Code)
                if idx == expanded_row:
                    cols[i].code(value, language='python')
                    if cols[i].button('Collapse', key=f'collapse_{idx}'):
                        st.session_state.expanded_row = None
                else:
                    if cols[i].button('Show Code', key=f'expand_{idx}'):
                        st.session_state.expanded_row = idx
            else:
                cols[i].write(value)
        if cols[-2].button('Edit', key=f'edit_{idx}'):
            st.session_state.edit_index = idx
            st.session_state.edit_mode = True
        if cols[-1].button('Delete', key=f'delete_{idx}'):
            delete_entry(idx)
            st.success("Entry deleted!")
            st.experimental_rerun()  # Refresh the page to update the table

def expand_code(idx):
    st.session_state.expanded_row = idx

display_expandable_table(st.session_state.data)

# Edit entry section
if 'edit_mode' in st.session_state and st.session_state.edit_mode:
    st.header("Edit Entry")
    edit_index = st.session_state.edit_index
    entry = st.session_state.data.iloc[edit_index]
    
    date_input = st.date_input("Date", pd.to_datetime(entry['Date']))
    client_input = st.text_input("Client", entry['Client'])
    am_input = st.text_input("AM", entry['AM'])
    ticket_input = st.text_input("SF Ticket", entry['SF Ticket'])
    use_case_input = st.text_input("Use Case", entry['Use Case'])
    notes_input = st.text_area("Notes", entry['Notes'])
    code_input = st.text_area("Code", entry['Code'])
    
    if st.button("Update Entry"):
        update_entry(edit_index, date_input.strftime('%Y-%m-%d'), client_input, am_input, ticket_input, use_case_input, notes_input, code_input)
        st.success("Entry updated!")
        st.session_state.edit_mode = False
        st.experimental_rerun()  # Refresh the page to update the table

# User input section for adding new entries
if 'edit_mode' not in st.session_state or not st.session_state.edit_mode:
    st.header("Add New Entry")
    date_input = st.date_input("Date", datetime.today().date(), key='date_input')
    client_input = st.text_input("Client", "", key='client_input')
    am_input = st.text_input("AM", "", key='am_input')
    sf_input = st.text_input("SF Ticket", "", key='ticket_input')
    use_case_input = st.text_input("Use Case", "", key='use_case_input')
    notes_input = st.text_area("Notes", "", key='notes_input')
    code_input = st.text_area("Code", "", key='code_input')
    
    if st.button("Add Entry"):
        add_entry(date_input.strftime('%Y-%m-%d'), client_input, am_input, ticket_input, use_case_input, notes_input, code_input)
        st.success("Entry added!")
        # Clear input fields
        st.session_state.date_input = datetime.today().date()
        st.session_state.client_input = ""
        st.session_state.am_input = ""
        st.session_state.ticket_input = ""
        st.session_state.use_case_input = ""
        st.session_state.notes_input = ""
        st.session_state.code_input = ""

# No need for a separate delete entry section since each row now has a delete button
