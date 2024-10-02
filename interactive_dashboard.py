# interactive_dashboard_streamlit.py

import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from math import comb

# Set the page configuration
st.set_page_config(
    page_title="🔍 Ranking Algorithms Performance Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Title of the dashboard
st.title("🔍 Ranking Algorithms Performance Dashboard")

# Load the averaged CSV data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('/Users/deepak/mercor-monorepo/ml/enterprise_sort/ranking_results_avg.csv')
    except FileNotFoundError:
        st.error("The file 'ranking_results_avg.csv' was not found in the current directory.")
        st.stop()
    
    # Ensure correct data types
    expected_columns = ['Noise Level', 'Num_Items', 'Num_Pairs', 'Algorithm', 'Top-n', 'Accuracy']
    for col in expected_columns:
        if col not in df.columns:
            st.error(f"Missing expected column: '{col}' in the CSV file.")
            st.stop()
    
    df['Noise Level'] = df['Noise Level'].astype(float).round(2)
    df['Num_Items'] = df['Num_Items'].astype(int)
    df['Num_Pairs'] = df['Num_Pairs'].astype(int)
    df['Top-n'] = df['Top-n'].astype(int)
    df['Accuracy'] = df['Accuracy'].astype(float)
    
    return df

df = load_data()

# Sidebar for filters
st.sidebar.header("🔧 Filter Parameters")

# Slider for Noise Level
noise_min = df['Noise Level'].min()
noise_max = df['Noise Level'].max()
noise_step = 0.01
noise_value = st.sidebar.slider(
    "📊 Select Noise Level:",
    min_value=noise_min,
    max_value=noise_max,
    value=noise_min,
    step=noise_step,
    format="%.2f"
)

# Slider for Number of Items
items_min = df['Num_Items'].min()
items_max = df['Num_Items'].max()
items_step = 100
items_value = st.sidebar.slider(
    "📈 Select Number of Items:",
    min_value=items_min,
    max_value=items_max,
    value=items_min,
    step=items_step,
    format="%d"
)

# Calculate the maximum possible pairs for the selected number of items
max_possible_pairs = comb(items_value, 2)

# Slider for Number of Pairs
pairs_min = df['Num_Pairs'].min()
pairs_max = df['Num_Pairs'].max()
pairs_step = 100
pairs_value = st.sidebar.slider(
    "🔢 Select Number of Pairs:",
    min_value=pairs_min,
    max_value=min(pairs_max, max_possible_pairs),
    value=pairs_min,
    step=pairs_step,
    format="%d"
)

# Validate Num_Pairs does not exceed C(Num_Items, 2)
if pairs_value > max_possible_pairs:
    st.sidebar.error(f"Number of Pairs cannot exceed C({items_value}, 2) = {max_possible_pairs}.")
    st.stop()

# Filter the dataframe based on selections
filtered_df = df[
    (df['Noise Level'] == noise_value) &
    (df['Num_Items'] == items_value) &
    (df['Num_Pairs'] == pairs_value)
]

# Check if the filtered dataframe is empty
if filtered_df.empty:
    st.warning("⚠️ No data available for the selected parameters.")
    st.stop()

# Further filter Top-n to be at most Num_Items
filtered_df = filtered_df[filtered_df['Top-n'] <= items_value]

# Get list of algorithms
algorithms = filtered_df['Algorithm'].unique()

# Create a Plotly figure
fig = go.Figure()

# Define color palette
from plotly.colors import qualitative

colors = qualitative.Dark24

for idx, alg in enumerate(algorithms):
    alg_data = filtered_df[filtered_df['Algorithm'] == alg].sort_values('Top-n')
    fig.add_trace(go.Scatter(
        x=alg_data['Top-n'],
        y=alg_data['Accuracy'],
        mode='lines+markers',
        name=alg,
        line=dict(color=colors[idx % len(colors)], width=2),
        marker=dict(size=8)
    ))

# Update layout
fig.update_layout(
    title=f"📈 Top-n Accuracy at Noise Level {noise_value}, Num_Items {items_value}, Num_Pairs {pairs_value}",
    xaxis_title="Top-n Candidates",
    yaxis_title="Accuracy",
    hovermode="closest",
    template="plotly_white",
    legend=dict(title="Algorithms"),
    width=900,
    height=600
)

# Display the Plotly figure
st.plotly_chart(fig, use_container_width=True)

# Display the selected parameters
st.sidebar.markdown("---")
st.sidebar.markdown(f"**📊 Selected Noise Level:** {noise_value}")
st.sidebar.markdown(f"**📈 Selected Number of Items:** {items_value}")
st.sidebar.markdown(f"**🔢 Selected Number of Pairs:** {pairs_value}")

# Optional: Display the underlying data
with st.expander("📄 Show Data"):
    st.write(filtered_df)
