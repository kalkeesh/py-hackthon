streamlit run mongo2.py &

sleep 3

uvicorn api:app --reload &

sleep 3

start hackathon.html