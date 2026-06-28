import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Clean Pipeline Optimizer")

st.title("🏭 Factory 2.0: Dynamic Priority Optimizer")
st.write("Use the table below to add, delete, or modify your project pipelines. Benefit types are auto-converted to dollar amounts instantly.")

# --------------------------------------------------------------------
# 🎛️ GLOBAL FINANCIAL MULTIPLIERS (THE SIDEBAR MONETARY CONVERTERS)
# --------------------------------------------------------------------
st.sidebar.header("🌍 Global Financial Multipliers")
st.sidebar.write("Configure the dollar values used to translate your benefits matrix:")

fte_dollar_value = st.sidebar.number_input("Value per 1.0 FTE (SGD/Yr)", value=80000, step=5000)
scrap_dollar_value = st.sidebar.number_input("Value per 1% Scrap Reduction (SGD/Yr)", value=15000, step=1000)
schedule_dollar_value = st.sidebar.number_input("Value per 1% Schedule Adherence (SGD/Yr)", value=120000, step=5000)
safety_ergonomic_value = st.sidebar.number_input("Value per Ergonomic/Safety Fix (SGD/Yr)", value=25000, step=5000)

# Weights
st.sidebar.subheader("🎯 Prioritization Weighting Index")
w_roi = st.sidebar.slider("Financial ROI Weight (%)", 0, 100, 40) / 100
w_trl = st.sidebar.slider("Technical Readiness (TRL) Weight (%)", 0, 100, 30) / 100
w_time = st.sidebar.slider("Speed to Value Weight (%)", 0, 100, 15) / 100
w_scale = st.sidebar.slider("Scalability Footprint Weight (%)", 0, 100, 15) / 100

# --------------------------------------------------------------------
# 📋 THE DYNAMIC FILL-IN-THE-BLANK DATA ENGINE
# --------------------------------------------------------------------
st.subheader("📝 Opportunity Pipeline Workspace")
st.caption("💡 To **Add a row**, scroll to the bottom of the table and click the empty row. To **Delete**, click the row index and hit Delete on your keyboard.")

# Baseline layout - now includes editable Status/Strategy column
initial_data = [
    {"Opportunity": "A. Smart Visual Inspection", "Status/Strategy": "co-develop with ARTC", "TRL": 6, "Est_Cost_SGD": 450000, "Benefit_Type": "Quality/Scrap Reduction", "Benefit_Quantity": 5.0, "Time_Months": 9, "Main_Risk": "Process integration", "Scale_Up_Sites": 4},
    {"Opportunity": "B. Robotics Automation", "Status/Strategy": "progress", "TRL": 4, "Est_Cost_SGD": 700000, "Benefit_Type": "FTE Savings", "Benefit_Quantity": 2.0, "Time_Months": 12, "Main_Risk": "High process variability", "Scale_Up_Sites": 6},
    {"Opportunity": "C. AI Production Scheduling", "Status/Strategy": "buy", "TRL": 5, "Est_Cost_SGD": 300000, "Benefit_Type": "Schedule Improvement", "Benefit_Quantity": 5.0, "Time_Months": 6, "Main_Risk": "Data quality & IT adoption", "Scale_Up_Sites": 3},
    {"Opportunity": "D. Autonomous Transport", "Status/Strategy": "exploratory study", "TRL": 7, "Est_Cost_SGD": 550000, "Benefit_Type": "FTE Savings", "Benefit_Quantity": 1.0, "Time_Months": 8, "Main_Risk": "EHS layout constraints", "Scale_Up_Sites": 5},
    {"Opportunity": "E. AR/VR Training", "Status/Strategy": "pause", "TRL": 6, "Est_Cost_SGD": 150000, "Benefit_Type": "Ergonomic/Safety/Other", "Benefit_Quantity": 1.0, "Time_Months": 4, "Main_Risk": "OT Hardware validation", "Scale_Up_Sites": 8},
    {"Opportunity": "F. Real-Time Quality Sensor", "Status/Strategy": "co-develop with ARTC", "TRL": 3, "Est_Cost_SGD": 250000, "Benefit_Type": "Quality/Scrap Reduction", "Benefit_Quantity": 10.0, "Time_Months": 18, "Main_Risk": "Low technology maturity", "Scale_Up_Sites": 4},
]
base_df = pd.DataFrame(initial_data)

strategy_options = ["buy", "co-develop with ARTC", "progress", "exploratory study", "pause"]

edited_df = st.data_editor(
    base_df,
    column_config={
        "Opportunity": st.column_config.TextColumn("1) Opportunity"),
        "Status/Strategy": st.column_config.SelectboxColumn("Overwrite Strategy Directive", options=strategy_options, default="exploratory study"),
        "TRL": st.column_config.NumberColumn("2) TRL", min_value=1, max_value=9, step=1, default=5),
        "Est_Cost_SGD": st.column_config.NumberColumn("3) Est Cost (SGD)", min_value=0, default=100000),
        "Benefit_Type": st.column_config.SelectboxColumn("4) Benefit Category", options=["FTE Savings", "Quality/Scrap Reduction", "Schedule Improvement", "Ergonomic/Safety/Other"], default="FTE Savings"),
        "Benefit_Quantity": st.column_config.NumberColumn("Benefit Quantity Unit", min_value=0.0, step=0.5, default=1.0),
        "Time_Months": st.column_config.NumberColumn("5) Time (Months)", min_value=1, default=6),
        "Main_Risk": st.column_config.TextColumn("6) Main Risk", default="To be evaluated"),
        "Scale_Up_Sites": st.column_config.NumberColumn("7) Scale-up (Sites)", min_value=1, default=1),
    },
    hide_index=False,
    num_rows="dynamic",
    use_container_width=True
)

# --------------------------------------------------------------------
# 🧠 THE TRANSLATION ENGINE & ALGORITHM RANKING
# --------------------------------------------------------------------
if not edited_df.empty and edited_df["Opportunity"].dropna().any():
    
    def convert_label_to_dollars(row):
        b_type = row["Benefit_Type"]
        b_qty = row["Benefit_Quantity"]
        if b_type == "FTE Savings":
            return b_qty * fte_dollar_value
        elif b_type == "Quality/Scrap Reduction":
            return b_qty * scrap_dollar_value
        elif b_type == "Schedule Improvement":
            return b_qty * schedule_dollar_value
        elif b_type == "Ergonomic/Safety/Other":
            return b_qty * safety_ergonomic_value
        return 0

    # Financial translation engine
    edited_df["Annual_Benefit_Per_Site_SGD"] = edited_df.apply(convert_label_to_dollars, axis=1)
    edited_df["Total_Portfolio_Benefit_SGD"] = edited_df["Annual_Benefit_Per_Site_SGD"] * edited_df["Scale_Up_Sites"]
    edited_df["Dynamic_ROI_Ratio"] = edited_df["Total_Portfolio_Benefit_SGD"] / edited_df["Est_Cost_SGD"].replace(0, 1)

    # Pre-Assessment Floor Gate
    edited_df["Status"] = edited_df["Dynamic_ROI_Ratio"].apply(
        lambda x: "🟢 Qualified" if x >= 1.0 else "❌ Below Financial Floor"
    )

    # Relative ranking segregation logic
    qualified_mask = edited_df["Status"] == "🟢 Qualified"
    
    if qualified_mask.any():
        qualified_df = edited_df[qualified_mask].copy()
        qualified_df["Score_ROI"] = pd.qcut(
            qualified_df["Dynamic_ROI_Ratio"], 
            q=max(2, len(qualified_df)), 
            labels=False, 
            duplicates='drop'
        ) + 1
    else:
        qualified_df = pd.DataFrame(columns=edited_df.columns.tolist() + ["Score_ROI"])

    disqualified_df = edited_df[~qualified_mask].copy()
    if not disqualified_df.empty:
        disqualified_df["Score_ROI"] = 0

    edited_df = pd.concat([qualified_df, disqualified_df], ignore_index=True)

    # Standardized dimension scoring
    edited_df["Score_TRL"] = (edited_df["TRL"] / 9) * 5
    edited_df["Score_Time"] = ((24 - edited_df["Time_Months"]).clip(lower=1) / 24) * 5
    edited_df["Score_Scale"] = (edited_df["Scale_Up_Sites"] / 10).clip(upper=1) * 5

    # Core weighted prioritization engine
    edited_df["Final_Priority_Score"] = edited_df.apply(
        lambda row: ((row["Score_ROI"] * w_roi) + (row["Score_TRL"] * w_trl) + 
                     (row["Score_Time"] * w_time) + (row["Score_Scale"] * w_scale))
                    if row["Status"] == "🟢 Qualified" else 0.0, axis=1
    )

    final_ranked_df = edited_df.sort_values(by="Final_Priority_Score", ascending=False).reset_index(drop=True)

    # 🚀 THE AGILE RATIONALE ENGINE: Generates text contextually based on live workspace states
    def generate_agile_rationale(row):
        opportunity = row["Opportunity"]
        strategy = row["Status/Strategy"]
        status = row["Status"]
        roi = row["Dynamic_ROI_Ratio"]
        risk = row["Main_Risk"]
        trl = row["TRL"]
        sites = row["Scale_Up_Sites"]
        
        # Scenario A: Failed absolute financial benchmark
        if status == "❌ Below Financial Floor":
            return (
                f"Defunded at primary screening. The total portfolio benefit fails to cover the estimated costs "
                f"(ROI Ratio of {roi:.2f}x). To qualify, this initiative requires cost-restructuring, "
                f"higher yield targets, or an alternative ecosystem framework to share capital risk."
            )
        
        # Scenario B: Evaluated on the active configuration choice
        if strategy == "buy":
            return (
                f"Top-tier choice. Delivers a verified financial return footprint across the network with an ROI "
                f"ratio of {roi:.2f}x. Highly compressed implementation timeline warrants an off-the-shelf procurement approach "
                f"('Buy') to capture rapid Horizon 1 value adjustments without long software engineering backlogs."
            )
            
        elif strategy == "co-develop with ARTC":
            return (
                f"High long-term asset value potential, but currently constrained by lower-maturity parameters (TRL {trl:g}) "
                f"and operational concerns regarding '{risk}'. Co-developing with ARTC permits shared access to public-private advanced laboratories, "
                f"external prototyping grants, and balanced deployment engineering risk structures."
            )
            
        elif strategy == "progress":
            return (
                f"Strong active qualification with an ROI ratio of {roi:.2f}x. Because the core hurdle involves managing "
                f"'{risk}', execution strategy remains fully internal ('Progress') to shield sensitive workflows, "
                f"protect manufacturing workspace IP, and control customized technical integration."
            )
            
        elif strategy == "exploratory study":
            return (
                f"Technology framework is mature (TRL {trl:g}), but deployment maps show outstanding operational constraints: "
                f"'{risk}'. A front-end structural site audit and targeted exploratory research study are recommended to resolve "
                f"integration parameters prior to heavy resource provisioning."
            )
            
        elif strategy == "pause":
            return (
                f"Yields marginal programmatic value over cost requirements ({roi:.2f}x ROI), but introduces compounding implementation overhead "
                f"across {sites} scaling target sites alongside critical bottlenecks linked to '{risk}'. Strategic 'Pause' active to preserve "
                f"available engineer hours for higher-priority portfolio deployments."
            )
            
        return "Operational data validated. Awaiting strategic categorization matrix adjustments."

    # Generate calculations and strings based on active rows
    final_ranked_df["Strategic Rationale & Technical Logic"] = final_ranked_df.apply(generate_agile_rationale, axis=1)
    final_ranked_df["Total Portfolio Benefit"] = final_ranked_df["Total_Portfolio_Benefit_SGD"].map("SGD ${:,.2f}".format)
    final_ranked_df["Est Cost"] = final_ranked_df["Est_Cost_SGD"].map("SGD ${:,.2f}".format)

    # --------------------------------------------------------------------
    # 📺 CLEAN PRESENTATION LAYER (OUTPUT MATRICES)
    # --------------------------------------------------------------------
    st.markdown("---")
    st.subheader("📊 Prioritized Investment Pipeline Output")
    
    if final_ranked_df.iloc[0]["Final_Priority_Score"] > 0:
        st.success(f"🚀 **Strategic Directive:** Your top-ranked viable initiative is **{final_ranked_df.iloc[0]['Opportunity']}**.")
    else:
        st.warning("⚠️ **Strategic Alert:** No initiatives currently meet the absolute minimum financial ROI floor of 1.0.")

    # 1. Primary Priority Table
    st.dataframe(
        final_ranked_df[[
            "Opportunity", "Status/Strategy", "Status", "Final_Priority_Score", 
            "Total Portfolio Benefit", "Est Cost", "TRL", "Time_Months", "Scale_Up_Sites", "Main_Risk"
        ]],
        use_container_width=True, hide_index=True
    )

    # 2. Dynamic Rationale Table
    st.write("")
    st.subheader("📋 Executive Decision Rationale & Logic Matrix")
    st.markdown("This governance layer dynamically reflects changes in risk, TRL, or financial ratios made in the workspace above.")
    
    st.dataframe(
        final_ranked_df[[
            "Opportunity", "Status/Strategy", "Status", "Main_Risk", "Strategic Rationale & Technical Logic"
        ]],
        column_config={
            "Opportunity": st.column_config.TextColumn("Initiative"),
            "Status/Strategy": st.column_config.TextColumn("Status / Strategy"),
            "Status": st.column_config.TextColumn("Financial Status"),
            "Main_Risk": st.column_config.TextColumn("Primary Bottleneck Risk"),
            "Strategic Rationale & Technical Logic": st.column_config.TextColumn("Strategic Rationale (Dynamic Engine)")
        },
        use_container_width=True, hide_index=True
    )
else:
    st.info("💡 Add a project row in the workspace table above to generate the prioritized ranking pipeline.")