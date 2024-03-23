import os
import streamlit as st
import pandas as pd
import subprocess
import base64
from datetime import datetime
from pymongo import MongoClient
import pandas as pd
from streamlit_ace import st_ace

# MongoDB connection details
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "hackathon"
COLLECTION_NAME = "round2"
EXCEL_FILE_PATH = 'Hackathon.xlsx'

def authenticate_user(username, password):
    users = {"user1": "password1", 
             "user2": "password2", 
             "user3": "password3",
             "user4": "password4",
             "user5": "password5", 
             }
    return username in users and users[username] == password

# def conduct_test(user_id, test_info, display_output=True):
#     user_data = {}
#     score = 0
#     output_data = {}  # Store outputs for validation
#     for i, info in enumerate(test_info, start=1):
#         question = info[0]
#         expected_answer = info[1]
#         code_to_run = info[2] if len(info) > 2 else None
        
#         st.subheader(f"Q {i}: {question}")
#         if code_to_run:
#             st.code(f"#Reference code: {code_to_run}", language="python")
        
#         user_code = st_ace(
#             placeholder=f"Write your code for Question {i} here...",
#             language="python",
#             theme="chrome",
#             key=f"{user_id}_question_{i}",
#             height=200
#         )
        
#         try:
#             process = subprocess.run(['python', '-c', user_code], capture_output=True, text=True)
#             output = process.stdout.strip()
#             error_output = process.stderr.strip()
#             output_data[f"question{i}"] = output  # Store output for validation
#             if display_output:
#                 if not error_output:
#                     st.success(f"Output for Question {i}:\n{output}")
#                 else:
#                     st.warning(f"Error for Question {i}:\n{error_output}")
#                 # Display output inline with code
#                 st.code(f"Output:\n{output}", language="python")
#         except Exception as e:
#             st.warning(f"Unexpected error for Question {i}:\n{e}")
#             st.code(f"Error:\n{str(e)}", language="python")
        
#         if output.strip() == expected_answer.strip() and not error_output:
#             score += 10
#         user_data[f"question{i}_usercode"] = user_code
#     return score, user_data, output_data



def conduct_test(user_id, test_info):
    user_data = {}
    score = 0
    for i, info in enumerate(test_info, start=1):
        question = info[0]
        expected_answer = info[1]
        code_to_run = info[2] if len(info) > 2 else None
        
        st.subheader(f"Q {i}: {question}")
        if code_to_run:
            st.code(f"#Reference code: {code_to_run}", language="python")
        
        user_code = st_ace(
            placeholder=f"Write your code for Question {i} here...",
            language="python",
            theme="chrome",
            key=f"{user_id}_question_{i}",
            height=200
        )
        
        try:
            process = subprocess.run(['python', '-c', user_code], capture_output=True, text=True)
            output = process.stdout.strip()
            error_output = process.stderr.strip()
            if error_output:
            #     pass
            #     # st.success(f"Output for Question {i}:\n{output}")
            # else:
                st.warning(f"Error for Question {i}:\n{error_output}")
            #Display output inline with code
            st.code(f"Output:\n{output}", language="python")
        except Exception as e:
            st.warning(f"Unexpected error for Question {i}:\n{e}")
            st.code(f"Error:\n{str(e)}", language="python")
        
        if output.strip() == expected_answer.strip() and not error_output:
            score += 10
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

# def append_to_excel(scores):
#     try:
#         if os.path.isfile(EXCEL_FILE_PATH):
#             existing_df = pd.read_excel(EXCEL_FILE_PATH)
#             for user_id, score in scores.items():
#                 if user_id in existing_df['User ID'].values:
#                     st.warning(f"Score for user {user_id} already exists in Excel! Skipping...")
#                 else:
#                     new_row = pd.DataFrame({'User ID': [user_id], 'Score': [score], 'Timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")]})
#                     existing_df = pd.concat([existing_df, new_row], ignore_index=True)
            
#             existing_df.sort_values(by=['Score', 'Timestamp'], ascending=[False, True], inplace=True)
#             existing_df.to_excel(EXCEL_FILE_PATH, index=False)
#             st.success("Data stored successfully in Excel!")
#         else:
#             df = pd.DataFrame(list(scores.items()), columns=['User ID', 'Score'])
#             df['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
#             df.sort_values(by=['Score', 'Timestamp'], ascending=[False, True], inplace=True)
#             df.to_excel(EXCEL_FILE_PATH, index=False)
#             st.success("Data stored successfully in Excel!")
#     except Exception as e:
#         st.error(f"Failed to store data in Excel: {e}")

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
        print(f"Error occurred while writing to Excel: {e}")


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
                    """# write code to display the first 5 rows of the dataframe using a pandas function """,
                    """
Name  Age  Grade Gender
0    kalki   20     85      M
1    vamsi   12     90      M
2  shekhar   16     78      M
3   kalyan   20     92      M
4    vijju   22     87      F""",
                    """ 
import pandas as pd
data = {
    'Name': ['kalki', 'vamsi', 'shekhar', 'kalyan', 'vijju', 'ragava', 'rajesh', 'varun', 'murthy', 'ramesh', 'suresh', 'naidu', 'josie', 'mia', 'sam', 'alyx', 'miho', 'eva', 'valli', 'natasha'],
    'Age': [20, 12, 16, 20, 22, 21, 19, 17, 19, 18, 20, 11, 19, 21, 15, 18, 19, 16, 20, 22],
    'Grade': [85, 90, 78, 92, 87, 88, 75, 95, 82, 91, 89, 93, 80, 94, 85, 90, 77, 92, 86, 88],
    'Gender': ['M', 'M', 'M', 'M', 'F', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F']
}
df = pd.DataFrame(data)
                    """
                ),
                (
                    """print a minor_df that contains all age below 18 and major_df age equal and above 18""",
                    """
Name  Age  Grade Gender
1     vamsi   12     90      M
2   shekhar   16     78      M
7     varun   17     95      M
11    naidu   11     93      M
14      sam   15     85      F
17      eva   16     92      F

       Name  Age  Grade Gender
0     kalki   20     85      M
3    kalyan   20     92      M
4     vijju   22     87      F
5    ragava   21     88      M
6    rajesh   19     75      M
8    murthy   19     82      M
9    ramesh   18     91      M
10   suresh   20     89      M
12    josie   19     80      F
13      mia   21     94      F
15     alyx   18     90      F
16     miho   19     77      F
18    valli   20     86      F
19  natasha   22     88      F
""",
                    """
import pandas as pd
data = {
    'Name': ['kalki', 'vamsi', 'shekhar', 'kalyan', 'vijju', 'ragava', 'rajesh', 'varun', 'murthy', 'ramesh', 'suresh', 'naidu', 'josie', 'mia', 'sam', 'alyx', 'miho', 'eva', 'valli', 'natasha'],
    'Age': [20, 12, 16, 20, 22, 21, 19, 17, 19, 18, 20, 11, 19, 21, 15, 18, 19, 16, 20, 22],
    'Grade': [85, 90, 78, 92, 87, 88, 75, 95, 82, 91, 89, 93, 80, 94, 85, 90, 77, 92, 86, 88],
    'Gender': ['M', 'M', 'M', 'M', 'F', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F']
}
df = pd.DataFrame(data)
#minor_df should contain all name, age ,grade and gender of the all who are below age 18
#minor_df = df[____________]
print(minor_df)
print()
#major_df should contain all name, age ,grade and gender of the all who are below age 18
#major_df = df[____________]
print(major_df)
"""
                ),
                (
                    """print a df that of minors who are male""",
                    """
Name  Age  Grade Gender
1     vamsi   12     90      M
2   shekhar   16     78      M
7     varun   17     95      M
11    naidu   11     93      M""",
                    """
import pandas as pd
data = {
    'Name': ['kalki', 'vamsi', 'shekhar', 'kalyan', 'vijju', 'ragava', 'rajesh', 'varun', 'murthy', 'ramesh', 'suresh', 'naidu', 'josie', 'mia', 'sam', 'alyx', 'miho', 'eva', 'valli', 'natasha'],
    'Age': [20, 12, 16, 20, 22, 21, 19, 17, 19, 18, 20, 11, 19, 21, 15, 18, 19, 16, 20, 22],
    'Grade': [85, 90, 78, 92, 87, 88, 75, 95, 82, 91, 89, 93, 80, 94, 85, 90, 77, 92, 86, 88],
    'Gender': ['M', 'M', 'M', 'M', 'F', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F']
}
df = pd.DataFrame(data)
#mdf should contain all name, age ,grade and gender of the all the males who are minors(aged below 18)
#mdf =minor_df[minor_df[_______]==___]
print(mdf)
"""
                ),
                (
                    """print a data frame with age and name columns """,
                    """
Name  Age
0     kalki   20
1     vamsi   12
2   shekhar   16
3    kalyan   20
4     vijju   22
5    ragava   21
6    rajesh   19
7     varun   17
8    murthy   19
9    ramesh   18
10   suresh   20
11    naidu   11
12    josie   19
13      mia   21
14      sam   15
15     alyx   18
16     miho   19
17      eva   16
18    valli   20
19  natasha   22""",
                    """
#selected columns should contain only name and Age columns in it
selected_columns = df[[__________]]
print(selected_columns)
"""
                ),
                (
                    """display the value of the cell at the 4th row and 2nd column in the DataFrame using function with index location?""",
                    """
Value at 4th row and 2nd column: 20
""",
                    """
import pandas as pd
data = {
    'Name': ['kalki', 'vamsi', 'shekhar', 'kalyan', 'vijju', 'ragava', 'rajesh', 'varun', 'murthy', 'ramesh', 'suresh', 'naidu', 'josie', 'mia', 'sam', 'alyx', 'miho', 'eva', 'valli', 'natasha'],
    'Age': [20, 12, 16, 20, 22, 21, 19, 17, 19, 18, 20, 11, 19, 21, 15, 18, 19, 16, 20, 22],
    'Grade': [85, 90, 78, 92, 87, 88, 75, 95, 82, 91, 89, 93, 80, 94, 85, 90, 77, 92, 86, 88],
    'Gender': ['M', 'M', 'M', 'M', 'F', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'F', 'F', 'F', 'F', 'F', 'F', 'F', 'F']
}
df = pd.DataFrame(data)
#value = df.___[ _ , _ ]
print(f"Value at 4th row and 2nd column: {value}")
"""
                ),
                (
                    """fill in the blanks to generate marks of all students using numpy""",
                    """
Marks of all the students: ['85' '92' '78' '88' '96']""",
                    """
import numpy as np
data = np.array([
    ["vamsi", 85],
    ["kalki", 92],
    ["shekar", 78],
    ["kalyan", 88],
    ["peter", 96]
])
marks = data[____]
print("Marks of all the students:", marks)
"""
                ),
                (
                    "#write code to arrange the marks in ascending order by using numpy function",
                    """[78 85 88 92 96]""",
                    """
#write code to arrange the marks in ascending order by using numpy function and generate the below output"""
                ),
                (
                    "#write code to print maximum marks of all the mark",
                    "96",
                    """
import numpy as np
data = np.array([
    ["vamsi", 85],
    ["kalki", 92],
    ["shekar", 78],
    ["kalyan", 88],
    ["peter", 96]
])
#write code to print maximum marks of all the marks
#marks = data[:, 1].astype(int)
"""
                ),
                (
                    "#write a code to transpose a 2x3 matrix",
                    """
[[1 4]
 [2 5]
 [3 6]]""",
                    """
import numpy as np
matrix = np.array([[1, 2, 3],
                   [4, 5, 6]])

# Transpose the matrix
transposed_matrix = np.__________(matrix)
print(transposed_matrix)"""
                ),
                (
                    "# write code to create a 3x3 identity matrix using a numpy function",
                    """
[[1. 0. 0.]
 [0. 1. 0.]
 [0. 0. 1.]]""",
                    f"""
#write code to print 3x3 identity matrix using a numpy function
"""

                )
            ]
        }
        
        if 'submitted' not in state or not state['submitted']:
            # score, user_data, output_data = conduct_test(state['username'], test_data[state['username']])
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
