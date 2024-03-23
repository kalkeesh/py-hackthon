import os
import streamlit as st
import pandas as pd
import subprocess
import base64
from datetime import datetime

def authenticate_user(username, password):
    users = {"user1": "password1", 
             "user2": "password2", 
             "user3": "password3",
             "kalyan" : "123456",
             "Babli"  : "123456"
             }
    return username in users and users[username] == password

def conduct_test(test_data):
    scores = {}
    for user_id, test_info in test_data.items():
        score = 0
        st.subheader(f"Test for {user_id}:")
        for i, info in enumerate(test_info, start=1):
            question = info[0]
            expected_answer = info[1]
            code_to_run = info[2] if len(info) > 2 else ""
            st.code(f"Question {i}: {question}\n{code_to_run}", language="python")
            user_code = st.text_area(f"Your code for Question {i}:", height=200)
            try:
                process = subprocess.run(['python', '-c', user_code], capture_output=True, text=True)
                output = process.stdout.strip()
                error_output = process.stderr.strip()
                if not error_output:
                    st.success(f"Output for Question {i}:\n{output}")
                else:
                    st.warning(f"Error for Question {i}:\n{error_output}")
            except Exception as e:
                st.warning(f"Unexpected error for Question {i}:\n{e}")
            if output.strip() == expected_answer.strip() and not error_output:
                score += 10
        scores[user_id] = score
    return scores

def append_to_excel(scores):
    file_path = 'Hackathon.xlsx'
    if os.path.isfile(file_path):
        existing_df = pd.read_excel(file_path)
        for user_id, score in scores.items():
            if user_id in existing_df['User ID'].values:
                existing_df.loc[existing_df['User ID'] == user_id, 'Score'] = score
            else:
                new_row = pd.DataFrame({'User ID': [user_id], 'Score': [score], 'Timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")]})
                existing_df = pd.concat([existing_df, new_row], ignore_index=True)
        
        existing_df.sort_values(by=['Score', 'Timestamp'], ascending=[False, True], inplace=True)
        existing_df.to_excel(file_path, index=False)
    else:
        df = pd.DataFrame(list(scores.items()), columns=['User ID', 'Score'])
        df['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        df.sort_values(by=['Score', 'Timestamp'], ascending=[False, True], inplace=True)
        df.to_excel(file_path, index=False)

def main():
    state = st.session_state.setdefault('state', {})
    image_path = r"img\title.png"
    st.markdown(f'<img src="data:image/png;base64,{base64.b64encode(open(image_path, "rb").read()).decode()}"  width=700 >', unsafe_allow_html=True)

    if 'is_logged_in' not in state or not state['is_logged_in']:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if authenticate_user(username, password):
                state['is_logged_in'] = True
                state['username'] = username
                st.success("Login successful!")
                st.empty()
            else:
                st.error("Authentication failed. Please check your credentials.")
    else:
        test_data = {
            state['username']: [
                (
                    "Print 'Hello, World!' \n output: Hello, World!",
                    "Hello, World!",
                    ""
                ),
                (
                    "Calculate the sum of 2 + 2 \n  output: 4",
                    "4"
                )
            ]
        }
        scores = conduct_test(test_data)
        append_to_excel(scores)
        
        if st.button("Submit"):
            state['is_logged_in'] = False
            state['username'] = None
            st.experimental_rerun()

if __name__ == "__main__":
    main()
