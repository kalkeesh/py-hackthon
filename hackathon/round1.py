import os
import streamlit as st
import pandas as pd
import subprocess
import base64
from datetime import datetime
from pymongo import MongoClient


# MongoDB connection details
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "hackathon"
COLLECTION_NAME = "round1"
EXCEL_FILE_PATH = 'Hackathon.xlsx'

def authenticate_user(username, password):
    users = {"user1": "password1", 
             "user2": "password2", 
             "user3": "password3",
             "user4": "password4",
             "user5": "password5", 
             "user6": "password6", 
             "user7": "password7",
             "user8": "Password8",
             "user9": "password9", 
             "user10": "password10", 
             "user11": "password11",
             "user12": "password12",
             }
    return username in users and users[username] == password


def conduct_test(user_id, test_info):
    user_data = {}
    score = 0
    for i, info in enumerate(test_info, start=1):
        question = info[0]
        expected_answer = info[1]
        code_to_run = info[2] if len(info) > 2 else None
        
        st.subheader(f"Q {i}: {question}")
        # if expected_answer:
        #     st.code(f"Expected Answer: {expected_answer}", language="python")
        if code_to_run:
            st.code(f"#Reference code: {code_to_run}", language="python")
        
        user_code = st.text_area(f"Your code for Question {i}:", height=200, key=f"{user_id}question{i}")
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
        # Store user code for each question
        user_data[f"question{i}_usercode"] = user_code
    return score, user_data


def append_to_mongodb(user_id, score, user_data):
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        existing_data = collection.find_one({"user_id": user_id})
        if existing_data:
            st.warning("Data for this user already exists in MongoDB!")
            return

        data_to_insert = {
            "user_id": user_id,
            "score": score,
            "timestamp": datetime.now(),
            **user_data
        }
        collection.insert_one(data_to_insert)
        st.success("Data stored successfully in MongoDB!")
    except Exception as e:
        st.error(f"Failed to insert data into MongoDB: {e}")


def append_to_excel(scores):
    try:
        if os.path.isfile(EXCEL_FILE_PATH):
            existing_df = pd.read_excel(EXCEL_FILE_PATH)
            for user_id, score in scores.items():
                if user_id in existing_df['User ID'].values:
                    st.warning(f"Score for user {user_id} already exists in Excel! Skipping...")
                else:
                    new_row = pd.DataFrame({'User ID': [user_id], 'Score': [score], 'Timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")]})
                    existing_df = pd.concat([existing_df, new_row], ignore_index=True)
            
            existing_df.sort_values(by=['Score', 'Timestamp'], ascending=[False, True], inplace=True)
            existing_df.to_excel(EXCEL_FILE_PATH, index=False)
            st.success("Data stored successfully in Excel!")
        else:
            df = pd.DataFrame(list(scores.items()), columns=['User ID', 'Score'])
            df['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            df.sort_values(by=['Score', 'Timestamp'], ascending=[False, True], inplace=True)
            df.to_excel(EXCEL_FILE_PATH, index=False)
            st.success("Data stored successfully in Excel!")
    except Exception as e:
        st.error(f"Failed to store data in Excel: {e}")

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
                    """Print the sum of all elements in the nested list """,
                    "45",
                    """ 
l=[[1,2,3],[4,5,6],[7,8,9]]
c=0
for sublist in l:
    ____________
    c+=_
print(c)
                    """
                ),
                (
                    """Print the values of the dictionary whose keys start with 'a' """,
                    "5 7 ",
                    """
my_dict = {'apple': 5, 'banana': 10, 'avocado': 7, 'grape': 3}
for key, value in my_dict.items():
    if ___________:
        print(_,end=' ')
"""
                ),
                (
                    """Print the multiplication table for a given number and display its sum""",
                    "5 * 1 = 5 5 * 2 = 10 5 * 3 = 15 5 * 4 = 20 5 * 5 = 25 5 * 6 = 30 5 * 7 = 35 5 * 8 = 40 5 * 9 = 45 5 * 10 = 50 275",
                    """
num = 5
count=0
print(f"Multiplication table for {num}:")
for i in range(1, 11):
    print(f"{num} * {i} = {_}")
    _____
print(count)
"""
                ),
                (
                    """Print the sum of all values in the nested dictionary""",
                    "21",
                    """
nested_dict = {'a': {'x': 1, 'y': 2}, 'b': {'x': 3, 'y': 4}, 'c': {'x': 5, 'y': 6}}
total = 0
for key1, inner_dict in nested_dict.items():
    for key2, value in inner_dict.items():
        total += ___
print(total)
"""
                ),
                (
                    """print the unique even numbers from the list""",
                    "4 6 8 ",
                    """
l = [1,2,2,4,6,3,33,67,8,10,10]
for i in l:
    if ______ and l.count(i)==_:
        print(i,end=' ')
"""
                ),
                (
                    """Handle the ZeroDivisionError and print "Cannot divide by zero" instead of crashing""",
                    "Cannot divide by zero",
                    """
numerator = 10
denominator = 0

try:
    result = numerator / denominator
    print(result)
except ___ as e:
    print(_)"""
                ),
                (
                    "Use a bitwise operator to convert value1=10 into 40",
                    "40",
                    """
value1 = 10
shift = 2
_______________"""
                ),
                (
                    "Add a element 98 at the end of the tuple and print the updated tuple (user type conversion)",
                    "(10, 20, 30, 98)",
                    """
my_tuple = (10, 20, 30)
________
________
________
print(my_tuple)
"""
                ),
                (
                    "print the factors of the revese of given string 12",
                    "1 3 7 21 ",
                    f"""
s='12'
_____________
for i in range(1,s+1):
    if ______:
        print(i,end=' ')
"""

                ),
                (
                    "Print the last three characters of the string",
                    "ing",
                    """
my_string = "Python is amazing"
print(_)"""
                )
            ]
        }
        
        
        
        
        
        if 'submitted' not in state or not state['submitted']:
            score, user_data = conduct_test(state['username'], test_data[state['username']])
            if st.button("Submit"):
                append_to_mongodb(state['username'], score, user_data)
                append_to_excel({state['username']: score})  # Append to Excel after MongoDB insertion
                state['submitted'] = True
                state['is_logged_in'] = False
                state['username'] = None
                st.experimental_rerun()

if __name__ == "__main__":
    main()