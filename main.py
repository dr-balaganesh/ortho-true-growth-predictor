# STREAMLIT APP V1
# Growth-Adjusted Cephalometric Outcome Predictor
# Numeric-only | Z-score based | PDF generation included

import streamlit as st
import pandas as pd
from fpdf import FPDF

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Cephalometric Outcome Predictor", layout="wide")
st.title("Growth-Adjusted Cephalometric Outcome Predictor")
st.caption("Numeric separation of growth and treatment effects using age- and sex-matched reference standards")

# -----------------------------
# 1. PATIENT INPUTS
# -----------------------------
st.header("Patient Information")

col1, col2, col3 = st.columns(3)
with col1:
    age = st.number_input("Age at start (years)", min_value=5.0, max_value=18.0, step=1.0)
with col2:
    sex = st.selectbox("Sex", ["Male", "Female"])
with col3:
    duration = st.number_input("Treatment duration", min_value=0.1, step=0.1)

duration_unit = st.selectbox("Duration unit", ["Years", "Months"])
duration_years = duration / 12 if duration_unit == "Months" else duration
age_end = min(age + duration_years, 16)  # growth capped at 16

# -----------------------------
# 2. PARAMETER SELECTION
# -----------------------------
st.header("Select Cephalometric Parameters")

parameters = {
    "FMA": "°",
    "SNB": "°",
    "Co-Go": "mm",
    "Go-Pg": "mm",
    "Co-Pg": "mm",
    "ANS-Me": "mm",
    "ANS-PNS": "mm"
}

selected_params = []
cols = st.columns(4)
for i, p in enumerate(parameters):
    if cols[i % 4].checkbox(p):
        selected_params.append(p)

# -----------------------------
# 3. INPUT VALUES
# -----------------------------
st.header("Pre- and Post-Treatment Values")

input_data = {}
for p in selected_params:
    unit = parameters[p]
    c1, c2 = st.columns(2)
    with c1:
        pre = st.number_input(f"{p} Pre-treatment ({unit})", key=f"pre_{p}")
    with c2:
        post = st.number_input(f"{p} Post-treatment ({unit})", key=f"post_{p}")
    input_data[p] = {"pre": pre, "post": post}

# -----------------------------
# 4. GROWTH REFERENCE DATA (MEAN + SD)
# -----------------------------
# (Values taken from your reference images)

growth_data = {
    "FMA": {
        "Male": {6:(29.3,5.9),7:(30.1,5.9),8:(29.4,4.8),9:(29.5,5.5),10:(29.6,5.0),
                 11:(29.1,4.7),12:(29.4,5.5),13:(29.0,5.1),14:(27.7,5.8),
                 15:(28.5,6.2),16:(28.7,5.2)},
        "Female": {6:(29.4,4.5),7:(29.7,3.7),8:(28.6,3.8),9:(28.4,4.9),10:(28.9,4.2),
                   11:(28.8,4.4),12:(28.1,5.2),13:(26.0,4.3),14:(24.8,5.8),
                   15:(24.6,4.1),16:(25.8,3.0)}
    },
    "SNB": {
        "Male": {6:(76.5,2.6),7:(75.7,2.8),8:(76.3,2.8),9:(76.4,2.5),10:(76.5,2.5),
                 11:(76.5,2.6),12:(77.3,2.7),13:(77.5,3.0),14:(77.3,3.1),
                 15:(77.6,3.0),16:(78.2,3.9)},
        "Female": {6:(76.0,3.5),7:(76.3,3.1),8:(76.7,3.3),9:(76.5,3.4),10:(76.7,3.5),
                   11:(77.3,3.9),12:(77.7,3.4),13:(77.5,3.9),14:(77.9,3.8),
                   15:(78.9,3.9),16:(79.2,2.3)}
    }
}

# -----------------------------
# HELPER: INTERPOLATION
# -----------------------------
def interpolate(param, sex, age):
    ages = sorted(growth_data[param][sex].keys())
    if age <= ages[0]:
        m, s = growth_data[param][sex][ages[0]]
        return m, s
    if age >= ages[-1]:
        m, s = growth_data[param][sex][ages[-1]]
        return m, s

    for i in range(len(ages) - 1):
        if ages[i] <= age <= ages[i + 1]:
            a1, a2 = ages[i], ages[i + 1]
            m1, s1 = growth_data[param][sex][a1]
            m2, s2 = growth_data[param][sex][a2]
            r = (age - a1) / (a2 - a1)
            return m1 + r * (m2 - m1), s1 + r * (s2 - s1)

# -----------------------------
# 5. COMPUTATION (Z-SCORE BASED)
# -----------------------------
results = []

for p in selected_params:
    if p not in growth_data:
        continue

    pre = input_data[p]["pre"]
    post = input_data[p]["post"]

    if pre == 0 or post == 0:
        continue

    mean_pre, sd_pre = interpolate(p, sex, age)
    mean_post, sd_post = interpolate(p, sex, age_end)

    z = (pre - mean_pre) / sd_pre if sd_pre != 0 else 0
    predicted_post = mean_post + z * sd_post

    predicted_growth = predicted_post - pre
    observed_change = post - pre
    treatment_effect = observed_change - predicted_growth

    results.append({
        "Parameter": p,
        "Pre": round(pre, 2),
        "Std Mean (Pre)": round(mean_pre, 2),
        "Std SD (Pre)": round(sd_pre, 2),
        "Post": round(post, 2),
        "Std Predicted (Post)": round(predicted_post, 2),
        "Predicted Growth Δ": round(predicted_growth, 2),
        "Observed Δ": round(observed_change, 2),
        "Treatment Δ": round(treatment_effect, 2)
    })

# -----------------------------
# 6. RESULTS DISPLAY
# -----------------------------
st.header("Results")

if results:
    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True)
else:
    st.info("Select parameters and enter pre- and post-treatment values.")

# -----------------------------
# 7. PDF GENERATION
# -----------------------------
def generate_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    pdf.cell(0, 8, "Growth-Adjusted Cephalometric Outcome Report", ln=True)
    pdf.ln(4)

    pdf.cell(0, 6, f"Age: {age} years | Sex: {sex}", ln=True)
    pdf.cell(0, 6, f"Treatment duration: {round(duration_years,2)} years", ln=True)
    pdf.ln(4)

    for _, row in df.iterrows():
        pdf.multi_cell(0, 6, str(row.to_dict()))

    pdf.ln(4)
    pdf.multi_cell(0, 6,
        "Predicted growth is calculated using Z-score–based longitudinal normalization "
        "from age- and sex-matched cephalometric reference standards."
    )

    return pdf

if results:
    if st.button("Generate PDF"):
        pdf = generate_pdf(df)
        st.download_button(
            "Download PDF",
            pdf.output(dest="S").encode("latin-1"),
            file_name="cephalometric_growth_report.pdf",
            mime="application/pdf"
        )
