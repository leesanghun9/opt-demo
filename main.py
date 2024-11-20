import random
import warnings

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from plotly.colors import qualitative
from plotly.subplots import make_subplots
from scipy.stats import beta


warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="optimisation demo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def run():

    if "df" not in st.session_state:
        st.session_state["df"] = pd.DataFrame(
            columns=["day", "segment", "variant", "success", "failure"]
        )
    if "day" not in st.session_state:
        st.session_state["day"] = 0

    # Title and Description
    st.title("Bayesian Optimization Tool Demo")
    st.write(
        "Optimize variant combinations with Bayesian statistics, using Thompson sampling."
    )

    # Experiment Configuration
    st.sidebar.header("Experiment Configuration")

    variants = st.sidebar.text_input(
        "Enter variants (comma-separated)", "Video, Text, Image"
    )
    variants = [v.strip() for v in variants.split(",")]

    # # Filter Configuration
    # st.sidebar.subheader("Record Filtering")
    filter_type = st.sidebar.selectbox(
        "Filter by", ["None", "Latest 1 months", "Latest 3 months"]
    )

    def filter_data(df):
        if filter_type == "Latest 1 months":
            max_day = df["day"].max()
            df = df[df["day"] >= max_day - 30]  # Assuming 1 day = 1 data entry
        elif filter_type == "Latest 3 months":
            max_day = df["day"].max()
            df = df[df["day"] >= max_day - 60]  # Assuming 1 day = 1 data entry
        return df

    def display_subplots(df, variants):
        fig = make_subplots(
            rows=1,
            cols=3,
            subplot_titles=[
                "Conversion Rate Distribution by Variant",
                "Traffic Over Time by Variant",
                "Conversion Rate Over Time by Variant",
            ],
        )

        colors = {
            variant: color
            for variant, color in zip(variants, qualitative.Plotly)
        }

        for i, variant in enumerate(variants):
            df_variant = df[df["variant"] == variant]

            # Beta distribution (Plot 1)
            a, b = df_variant.sum()[["success", "failure"]].values
            x = np.linspace(0, 1, 1000)
            y = beta(a + 1, b + 1).pdf(x)
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    mode="lines",
                    name=f"{variant} Distribution",
                    legendgroup=variant,
                    line=dict(color=colors[variant]),
                ),
                row=1,
                col=1,
            )

            # Traffic to date (Plot 2)
            df_variant["traffic_to_date"] = (
                df_variant["success"].cumsum() + df_variant["failure"].cumsum()
            )
            fig.add_trace(
                go.Scatter(
                    x=df_variant["day"],
                    y=df_variant["traffic_to_date"],
                    mode="lines+markers",
                    name=f"{variant} Traffic",
                    legendgroup=variant,
                    line=dict(color=colors[variant]),
                ),
                row=1,
                col=2,
            )

            # Conversion rate to date (Plot 3)
            df_variant["conversion_rate_to_date"] = (
                df_variant["success"].cumsum() / df_variant["traffic_to_date"]
            )
            fig.add_trace(
                go.Scatter(
                    x=df_variant["day"],
                    y=df_variant["conversion_rate_to_date"],
                    mode="lines+markers",
                    name=f"{variant} Conversion Rate",
                    legendgroup=variant,
                    line=dict(color=colors[variant]),
                ),
                row=1,
                col=3,
            )

        fig.update_layout(
            title="Variant Performance Analysis",
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.5,
                xanchor="center",
                x=0.5,
            ),
        )

        st.plotly_chart(fig)

    if st.button("Experient Initialise"):
        total_traffic = random.randint(100, 200)
        st.session_state["df"] = pd.DataFrame(
            columns=["day", "segment", "variant", "success", "failure"]
        )
        st.session_state["day"] = 0
        init_split = total_traffic // len(variants)
        # day = 0
        for variant in variants:
            mock_conversion_rate = np.random.normal(0.4, 0.05)
            loc = st.session_state["df"].shape[0]
            st.session_state["df"].loc[loc] = [
                st.session_state["day"],
                "segment1",
                variant,
                round(init_split * mock_conversion_rate),
                init_split - round(init_split * mock_conversion_rate),
            ]

        st.session_state["day"] += 1
        display_subplots(st.session_state["df"], variants)

    if st.button("Simulate"):

        # Thompson sampling
        total_traffic = random.randint(100, 200)
        df_sum = (
            st.session_state["df"]
            .groupby("variant")
            .sum()[["success", "failure"]]
        )
        traffic_allocation = {}
        beta_random = {}

        for variant in variants:
            traffic_allocation[variant] = 0

        for i in range(total_traffic):
            for variant in variants:
                beta_random[variant] = np.random.beta(
                    df_sum.loc[variant, "success"] + 1,
                    df_sum.loc[variant, "failure"] + 1,
                )

            traffic_allocation[pd.Series(beta_random).idxmax()] += 1

        # Simulation
        for variant in variants:
            traffic = traffic_allocation[variant]
            mock_conversion_rate = np.random.normal(0.4, 0.05)
            loc = st.session_state["df"].shape[0]
            st.session_state["df"].loc[loc] = [
                st.session_state["day"],
                "segment1",
                variant,
                round(traffic * mock_conversion_rate),
                traffic - round(traffic * mock_conversion_rate),
            ]
        st.session_state["day"] += 1
        display_subplots(st.session_state["df"], variants)

    st.session_state["df"] = filter_data(st.session_state["df"])

    ## TODO ADD RECORDS FILTERING LOGIC (LATEST 6 MONTH etc)
    ## TODO REARRANGE LAYOUT
    ## TODO ADD DATAFRAME FOR REF


if __name__ == "__main__":
    run()
