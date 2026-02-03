# STREAMLIT APP V1
# Growth-Adjusted Cephalometric Outcome Predictor
# Numeric-only | Z-score based | PDF generation included

import streamlit as st
import pandas as pd

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Cephalometric Outcome Predictor", layout="wide")
st.title("Growth-Adjusted Cephalometric Outcome Predictor")
st.caption(
    "Numeric separation of growth and treatment effects using pooled reference standards and age-adjusted prediction"
)

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
age_end = min(age + duration_years, 16)

# -----------------------------
# 2. PARAMETER SELECTION
# -----------------------------
st.header("Select Cephalometric Parameters")

parameters = {
    "FMA": "deg",
    "SNB": "deg",
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
# 4. GROWTH REFERENCE DATA
# -----------------------------
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
    },
    "Co-Go": {
        "Male": {6:(48.7,3.5),7:(49.1,3.4),8:(51.3,3.1),9:(52.8,3.3),10:(54.0,3.5),
                 11:(55.8,3.5),12:(57.2,3.9),13:(59.4,4.2),14:(61.6,4.4),
                 15:(62.7,4.1),16:(66.1,4.1)},
        "Female": {6:(46.5,2.9),7:(47.7,2.8),8:(49.1,2.9),9:(50.8,2.9),10:(51.5,2.7),
                   11:(52.4,2.8),12:(54.6,3.9),13:(55.1,3.8),14:(56.8,3.5),
                   15:(58.9,3.4),16:(60.5,2.4)}
    },
    "Go-Pg": {
        "Male": {6:(66.1,2.8),7:(68.9,3.0),8:(71.2,2.9),9:(73.0,2.7),10:(75.1,2.8),
                 11:(77.1,3.2),12:(78.5,3.4),13:(80.4,3.7),14:(82.8,4.0),
                 15:(84.3,4.1),16:(86.5,3.7)},
        "Female": {6:(66.1,4.2),7:(67.9,3.9),8:(70.4,4.2),9:(71.7,4.5),10:(74.0,4.2),
                   11:(75.7,4.2),12:(76.6,3.8),13:(78.4,4.0),14:(79.4,3.7),
                   15:(80.6,3.9),16:(81.5,3.8)}
    },
    "Co-Pg": {
        "Male": {6:(101.8,4.4),7:(104.1,3.5),8:(107.8,3.8),9:(109.9,4.0),10:(112.8,4.0),
                 11:(115.8,4.5),12:(117.9,4.8),13:(121.0,5.5),14:(124.1,5.9),
                 15:(126.3,5.1),16:(130.9,5.7)},
        "Female": {6:(98.9,4.3),7:(101.6,4.6),8:(104.5,5.0),9:(106.7,5.2),10:(109.5,4.9),
                   11:(111.6,4.9),12:(114.0,4.6),13:(116.1,3.9),14:(118.1,3.9),
                   15:(120.1,5.1),16:(121.4,3.9)}
    },
    "ANS-Me": {
        "Male": {6:(63.7,4.0),7:(65.5,4.4),8:(66.6,4.4),9:(67.3,4.3),10:(68.9,4.9),
                 11:(70.3,4.8),12:(71.1,5.1),13:(72.0,5.6),14:(74.3,5.8),
                 15:(76.7,6.4),16:(79.5,6.2)},
        "Female": {6:(61.6,3.9),7:(63.6,4.1),8:(63.5,4.2),9:(64.1,4.6),10:(65.3,4.9),
                   11:(65.8,4.6),12:(66.5,3.8),13:(68.1,4.5),14:(69.1,5.0),
                   15:(69.5,5.3),16:(69.3,5.2)}
    },
    "ANS-PNS": {
        "Male": {6:(50.2,2.2),7:(51.4,2.5),8:(52.1,2.9),9:(53.3,2.9),10:(54.4,2.6),
                 11:(56.0,2.4),12:(56.7,3.1),13:(57.8,3.0),14:(58.7,3.6),
                 15:(59.6,3.6),16:(61.6,3.7)},
        "Female": {6:(48.9,2.3),7:(50.5,2.9),8:(51.2,2.5),9:(51.2,3.2),10:(53.1,3.1),
                   11:(53.9,4.0),12:(54.1,3.2),13:(55.3,3.0),14:(56.7,2.9),
                   15:(57.1,2.7),16:(57.0,4.4)}
    }
}

# -----------------------------
# INTERPOLATION
# -----------------------------
def interpolate(param, sex, age):
    ages = sorted(growth_data[param][sex])
    if age <= ages[0]:
        return growth_data[param][sex][ages[0]]
    if age >= ages[-1]:
        return growth_data[param][sex][ages[-1]]
    for i in range(len(ages)-1):
        if ages[i] <= age <= ages[i+1]:
            a1, a2 = ages[i], ages[i+1]
            m1, s1 = growth_data[param][sex][a1]
            m2, s2 = growth_data[param][sex][a2]
            r = (age - a1) / (a2 - a1)
            return (m1 + r*(m2-m1), s1 + r*(s2-s1))

# -----------------------------
# POOLED STATS
# -----------------------------
def pooled_stats(param, sex):
    means = []
    sds = []
    for age in growth_data[param][sex]:
        m, s = growth_data[param][sex][age]
        means.append(m)
        sds.append(s)
    pooled_mean = sum(means) / len(means)
    pooled_sd = (sum([s**2 for s in sds]) / len(sds))**0.5
    return pooled_mean, pooled_sd

# -----------------------------
# COMPUTATION
# -----------------------------
results = []

for p in selected_params:
    pre = input_data[p]["pre"]
    post = input_data[p]["post"]

    if pre == 0 or post == 0:
        continue

    pooled_mean, pooled_sd = pooled_stats(p, sex)
    z = (pre - pooled_mean) / pooled_sd if pooled_sd else 0

    mean_post, sd_post = interpolate(p, sex, age_end)
    predicted_value = mean_post + z * sd_post

    expected_growth = predicted_value - pre
    observed_change = post - pre
    net_treatment_effect = observed_change - expected_growth

    results.append({
        "Parameter": p,
        "Pre Value": round(pre,2),
        "Pooled Mean Data": round(pooled_mean,2),
        "Pooled SD Data": round(pooled_sd,2),
        "Z Score": round(z,2),
        "Post Value": round(post,2),
        "Observed Change": round(observed_change,2),
        "Predicted Value": round(predicted_value,2),
        "Expected Growth": round(expected_growth,2),
        "Treatment Effect": round(net_treatment_effect,2)
    })


# -----------------------------
# RESULTS
# -----------------------------
st.header("Results")
if results:
    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True)
else:
    st.info("Enter values to see results.")

# -----------------------------
# PDF GENERATION
# -----------------------------
if results and st.button("Generate PDF"):
    from fpdf import FPDF

    def safe(t):
        return t.encode("latin-1", "replace").decode("latin-1")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    pdf.cell(0,8,safe("Growth-Adjusted Cephalometric Outcome Report"),ln=True)
    pdf.ln(4)
    pdf.cell(0,6,safe(f"Age: {age} | Sex: {sex} | Duration: {round(duration_years,2)} years"),ln=True)
    pdf.ln(4)

    for _, r in df.iterrows():
        pdf.multi_cell(0,6,safe(str(r.to_dict())))

    st.download_button(
        "Download PDF",
        pdf.output(dest="S").encode("latin-1"),
        file_name="cephalometric_growth_report.pdf",
        mime="application/pdf"
    )
