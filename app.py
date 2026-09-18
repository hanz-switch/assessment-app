import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Assessment Platform", layout="wide", initial_sidebar_state="expanded")

# --- INITIALIZE DATABASE IN SESSION STATE ---
if "assessments" not in st.session_state:
    st.session_state.assessments = pd.DataFrame(columns=[
        "Timestamp", "Region", "Store", "Quarter", "Month", "Crew_ID", "Topic",
        "RolePlay_Score", "Wayground_Score", "Result_Percent", "Score_Tier",
        "Remarks", "Trainer"
    ])

# --- MAPPING DATA ---
REGIONAL_DATA = {
    "Northern Malaysia": {
        "stores": ["UHNT", "UHJT", "UHGT", "URAN", "URDV", "URSU", "URQB", "URAC", "UHTS", "UHLN", "URKN", "UHGW"],
        "trainers": ["Annas", "Hanz"]
    },
    "Central Malaysia": {
        "stores": ["URBT", "URMK", "URKLMP", "URVE", "URPV", "URPTIC", "URSGAC", "URKLPD", "URKLPP", "URBJ", "URKE", "URKLAK", "UHSGEG", "UHSR"],
        "trainers": ["Adiputera", "Cornelia"]
    },
    "Southern Malaysia": {
        "stores": ["URTC", "URAM", "UHAU", "UHMU", "UHPT", "UHVB", "UHKG"],
        "trainers": ["Nabil"]
    },
    "East Coast Malaysia": {
        "stores": ["UREC", "UHBE", "UHKU", "UHTE"],
        "trainers": ["Adiputera"]
    },
    "East Malaysia: Sabah": {
        "stores": ["URTO", "UHBH", "UHTW", "URIG", "UHSBPQ", "UHSM"],
        "trainers": ["Puyang"]
    },
    "East Malaysia: Sarawak": {
        "stores": ["UHMD", "URVC", "URSP", "UHCO"],
        "trainers": ["Puyang"]
    }
}

TOPICS = [
    "iPadOS & macOS Coaching", "Apple Sports", "iPad Accessibility | Guided Access",
    "Pixel 10 | Quick Share with AirDrop", "iPhone 17 Series | Camera Control",
    "iPad + Students | Stay on tasks with Focus"
]

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio(
    "Go to",
    ["📊 Overview Dashboard", "📝 Submit Assessment", 
     "📍 Northern Malaysia", "📍 Central Malaysia", "📍 Southern Malaysia", 
     "📍 East Coast Malaysia", "📍 East Malaysia: Sabah", "📍 East Malaysia: Sarawak"]
)

st.sidebar.markdown("---")
# Export Feature
if not st.session_state.assessments.empty:
    csv = st.session_state.assessments.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("📥 Download Master CSV", data=csv, file_name="master_assessments.csv", mime="text/csv")


# Helper Function to Render Regional Dashboards
def render_regional_dashboard(region_name):
    st.title(f"📍 {region_name} Dashboard")
    df = st.session_state.assessments
    regional_df = df[df["Region"] == region_name]
    
    if regional_df.empty:
        st.info(f"No assessment submissions recorded yet for {region_name}.")
        return

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Assessments", len(regional_df))
    m2.metric("Average Score", f"{regional_df['Result_Percent'].mean():.2f}%")
    m3.metric("Pass Rate (>50%)", f"{(regional_df['Result_Percent'] >= 50).mean()*100:.1f}%")

    st.markdown("### Store Performance Breakdown")
    store_summary = regional_df.groupby("Store").agg(
        Submissions=("Crew_ID", "count"),
        Average_Score=("Result_Percent", "mean")
    ).reset_index()
    st.dataframe(store_summary, use_container_width=True)

    st.markdown("### Recent Submissions")
    st.dataframe(regional_df, use_container_width=True)


# --- PAGE 1: OVERVIEW DASHBOARD ---
if page == "📊 Overview Dashboard":
    st.title("📊 National Overview Dashboard")
    df = st.session_state.assessments

    if df.empty:
        st.warning("No data submitted yet across any region. Select '📝 Submit Assessment' from the side menu to begin.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Assessments", len(df))
        col2.metric("National Avg Score", f"{df['Result_Percent'].mean():.2f}%")
        col3.metric("Advanced Tiers (>80%)", len(df[df["Score_Tier"] == "Advanced"]))
        col4.metric("Weak Tiers (<50%)", len(df[df["Score_Tier"] == "Weak"]))

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Assessments by Region")
            st.bar_chart(df["Region"].value_counts())
        with c2:
            st.markdown("### Score Tier Breakdown")
            st.bar_chart(df["Score_Tier"].value_counts())

        st.markdown("### Master Assessment Logs")
        st.dataframe(df, use_container_width=True)

# --- PAGE 2: SUBMIT ASSESSMENT FORM ---
elif page == "📝 Submit Assessment":
    st.title("📝 Centralized Assessment Form")
    
    with st.form("assessment_form"):
        st.subheader("1. Assessment Details")
        col1, col2, col3 = st.columns(3)
        
        selected_region = col1.selectbox("Region*", list(REGIONAL_DATA.keys()))
        # Dynamic Store and Trainer updates based on selected Region
        available_stores = REGIONAL_DATA[selected_region]["stores"]
        available_trainers = REGIONAL_DATA[selected_region]["trainers"]
        
        selected_store = col2.selectbox("Store*", available_stores)
        crew_id = col3.text_input("Crew ID*", placeholder="Example: 1234")

        col4, col5, col6 = st.columns(3)
        quarter = col4.selectbox("Quarter*", ["Quarter 4, 2026", "Quarter 1, 2027"])
        month = col5.selectbox("Month*", ["October", "November", "December"])
        topic = col6.selectbox("Topic Assessed*", TOPICS)

        st.markdown("---")
        st.subheader("2. Assessment Check-up")
        
        # Role Play Matrix
        st.write("**Role-Play Rubric (1 = Poor, 5 = Exceptional)**")
        rp_c1, rp_c2, rp_c3, rp_c4 = st.columns(4)
        c_score = rp_c1.slider("Connect*", 1, 5, 3)
        d_score = rp_c2.slider("Discover*", 1, 5, 3)
        s_score = rp_c3.slider("Share*", 1, 5, 3)
        cl_score = rp_c4.slider("Close*", 1, 5, 3)
        
        rp_total = c_score + d_score + s_score + cl_score

        # Wayground Grid Select
        st.write("**Wayground Score (0 - 10 Grid)**")
        wayground_score = st.select_slider("Wayground Points*", options=list(range(0, 11)), value=5)

        # Real-time Score Auto-Calculation
        total_possible = 30
        calculated_percent = round(((wayground_score + rp_total) / total_possible) * 100, 2)
        
        # Auto Assign Score Tier
        if calculated_percent < 50:
            calculated_tier = "Weak"
        elif calculated_percent <= 80:
            calculated_tier = "On Par"
        else:
            calculated_tier = "Advanced"

        st.markdown("---")
        st.subheader("3. Automated Score Calculation")
        sc1, sc2 = st.columns(2)
        sc1.metric("Calculated Result (%)", f"{calculated_percent}%")
        sc2.metric("Assigned Score Tier", calculated_tier)

        st.markdown("---")
        st.subheader("4. Trainer Sign-off")
        remarks = st.text_area("Remarks / Feedback (If any)", placeholder="Nil")
        selected_trainer = st.radio("Trainer*", available_trainers, horizontal=True)

        submitted = st.form_submit_button("🚀 Submit Assessment")

        if submitted:
            if not crew_id:
                st.error("Please enter a valid Crew ID before submitting.")
            else:
                new_entry = {
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Region": selected_region,
                    "Store": selected_store,
                    "Quarter": quarter,
                    "Month": month,
                    "Crew_ID": crew_id,
                    "Topic": topic,
                    "RolePlay_Score": rp_total,
                    "Wayground_Score": wayground_score,
                    "Result_Percent": calculated_percent,
                    "Score_Tier": calculated_tier,
                    "Remarks": remarks if remarks else "Nil",
                    "Trainer": selected_trainer
                }
                st.session_state.assessments = pd.concat(
                    [st.session_state.assessments, pd.DataFrame([new_entry])], 
                    ignore_index=True
                )
                st.success(f"Assessment submitted successfully for Crew ID {crew_id} ({selected_region})!")

# --- REGIONAL PAGES ---
else:
    region_name = page.replace("📍 ", "")
    render_regional_dashboard(region_name)