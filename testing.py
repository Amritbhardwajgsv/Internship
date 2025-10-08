import streamlit as st

import matplotlib.pyplot as plt

st.title("AI-Based Metro Headway Simulation")

num_trains = st.slider("Number of Trains", 1, 10, 3)
sim_time = st.time_input("Start Time", value=None)

if st.button("Run Simulation"):
    result = run_simulation(num_trains, sim_time)
    st.write("Train Schedule:")
    st.dataframe(result['timetable'])

    st.write("Headway Violations:")
    st.dataframe(result['violations'])

    st.write("Train Movement Chart:")
    fig = result['plot']
    st.pyplot(fig)
