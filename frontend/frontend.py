import streamlit as st
import requests
import os

API_URL = os.environ.get("API_URL")

st.title("Notes App")

st.write("Your very own note taking app!")

# -----------------------------
# CREATE
# -----------------------------
st.header("Create a new note")
with st.form("create_note"):
    title = st.text_input("Title")
    content = st.text_area("Content")
    creator = st.text_input("Creator")
    submitted = st.form_submit_button("Create")
    
    if submitted:
        response = requests.post(
            f"{API_URL}/notes",
            json={"title": title, "content": content, "creator": creator}
        )
        if response.status_code == 200:
            st.success("Note created!")
        else:
            st.error(f"Error: {response.text}")

# -----------------------------
# READ
# -----------------------------
st.header("All Notes")
response = requests.get(f"{API_URL}/notes")
if response.status_code == 200:
    notes = response.json()
    for note in notes:
        with st.expander(f"{note['id']}: {note['title']} by {note.get('creator', 'Unknown')}"):
            st.write(f"**Content:** {note['content']}")
            
            # -----------------------------
            # UPDATE
            # -----------------------------
            with st.form(f"update_{note['id']}"):
                new_title = st.text_input("Title", value=note['title'])
                new_content = st.text_area("Content", value=note['content'])
                new_creator = st.text_input("Creator", value=note.get('creator', ''))
                update_btn = st.form_submit_button("Update")
                
                if update_btn:
                    resp = requests.put(
                        f"{API_URL}/notes/{note['id']}",
                        json={"title": new_title, "content": new_content, "creator": new_creator}
                    )
                    if resp.status_code == 200:
                        st.success("Note updated!")
                    else:
                        st.error(f"Error: {resp.text}")
            
            # -----------------------------
            # DELETE
            # -----------------------------
            delete_btn = st.button(f"Delete note {note['id']}")
            if delete_btn:
                resp = requests.delete(f"{API_URL}/notes/{note['id']}")
                if resp.status_code == 200:
                    st.success("Note deleted!")
                    st.rerun()
                else:
                    st.error(f"Error: {resp.text}")
else:
    st.error("Could not fetch notes")

