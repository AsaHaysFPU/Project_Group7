import streamlit as st
import pandas as pd

# Example distribution data from your logic module
# Replace this with your actual data
distribution_data = {
    "Category": ["A", "B", "C", "D"],
    "Count": [10, 25, 15, 30],
}

# Convert to a DataFrame
df = pd.DataFrame(distribution_data)

# Set the index so the bar chart labels come from the "Category" column
df = df.set_index("Category")

# Display the bar chart
st.bar_chart(df)