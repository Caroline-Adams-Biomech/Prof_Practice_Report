# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 18:38:52 2026

@author: Caroline Adams
"""

import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Speed Across the Sprint")

st.write(
    "This graph shows how running speed changes across "
    "each sprint split."
)

data = {
    "Trial": ["Trial 1", "Trial 1", "Trial 1", "Trial 2", "Trial 2"],
    "Split": ["0-10 m", "10-20 m", "20-30 m", "0-10 m", "10-20 m"],
    "Average Cycle Velocity (m/s)": [5.26, 9.52, 9.80, 5.21, 9.61]
}

df = pd.DataFrame(data)

selected_trials = st.multiselect(
    "Select trials to display",
    options=df["Trial"].unique(),
    default=df["Trial"].unique()
)

filtered_df = df[df["Trial"].isin(selected_trials)]

fig = px.line(
    filtered_df,
    x="Split",
    y="Average Cycle Velocity (m/s)",
    color="Trial",
    markers=True
)

st.plotly_chart(fig, use_container_width=True)