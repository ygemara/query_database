import json

# Function to add a new entry
def add_entry(date, client, am, sf, use_case, notes, code, report_id):
    try:
        formatted_code = json.dumps(json.loads(code), indent=4)
    except json.JSONDecodeError:
        st.error("Invalid JSON format in the Code field.")
        return
    
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
