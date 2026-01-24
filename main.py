# STREAMLIT APP V1
# Growth-Adjusted Cephalometric Outcome Predictor
# Numeric-only | No interpretation | PDF generation included

import streamlit as st
import pandas as pd
from fpdf import FPDF

st.set_page_config(page_title="Cephalometric Outcome Predictor", layout="wide")

st.title("Growth-Adjusted Cephalometric Outcome Predictor")
st.caption("Numeric separation of growth and treatment effects")

# -----------------------------
# 1. PATIENT INPUTS
# -----------------------------
st.header("Patient Information")

col1, col2, col3 = st.columns(3)
with col1:
    age = st.number_input("Age at start (years)", min_value=5, max_value=18, step=1)
with col2:
    sex = st.selectbox("Sex", ["Male", "Female"])
with col3:
    duration = st.number_input("Treatment duration", min_value=0.1, step=0.1)

duration_unit = st.selectbox("Duration unit", ["Years", "Months"])
if duration_unit == "Months":
    duration_years = duration / 12
else:
    duration_years = duration

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
for i, p in enumerate(parameters.keys()):
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
# 4. GROWTH MODEL (MEAN + SD WITH Z-SCORE)
# -----------------------------
# IMPORTANT:
# The dictionaries below MUST be populated with exact MEAN and SD values
# extracted from the reference images (age- and sex-specific).
# Structure:
# growth_data[parameter][sex][age] = {"mean": value, "sd": value}

# Example structure with illustrative dummy values ONLY.
# Replace these with exact values from the images before use.

growth_data = {
    # -------- FMA (deg) --------
    "FMA": {
        "Male": {
            6: {"mean": 29.3, "sd": 5.9},
            7: {"mean": 30.1, "sd": 5.9},
            8: {"mean": 29.4, "sd": 4.8},
            9: {"mean": 29.5, "sd": 5.5},
            10: {"mean": 29.6, "sd": 5.0},
            11: {"mean": 29.1, "sd": 4.7},
            12: {"mean": 29.4, "sd": 5.5},
            13: {"mean": 29.0, "sd": 5.1},
            14: {"mean": 27.7, "sd": 5.8},
            15: {"mean": 28.5, "sd": 6.2},
            16: {"mean": 28.7, "sd": 5.2}
        },
        "Female": {
            6: {"mean": 29.4, "sd": 4.5},
            7: {"mean": 29.7, "sd": 3.7},
            8: {"mean": 28.6, "sd": 3.8},
            9: {"mean": 28.4, "sd": 4.9},
            10: {"mean": 28.9, "sd": 4.2},
            11: {"mean": 28.8, "sd": 4.4},
            12: {"mean": 28.1, "sd": 5.2},
            13: {"mean": 26.0, "sd": 4.3},
            14: {"mean": 24.8, "sd": 5.8},
            15: {"mean": 24.6, "sd": 4.1},
            16: {"mean": 25.8, "sd": 3.0}
        }
    },

    # -------- SNB (deg) --------
    "SNB": {
        "Male": {
            6: {"mean": 76.5, "sd": 2.6},
            7: {"mean": 75.7, "sd": 2.8},
            8: {"mean": 76.3, "sd": 2.8},
            9: {"mean": 76.4, "sd": 2.5},
            10: {"mean": 76.5, "sd": 2.5},
            11: {"mean": 76.5, "sd": 2.6},
            12: {"mean": 77.3, "sd": 2.7},
            13: {"mean": 77.5, "sd": 3.0},
            14: {"mean": 77.3, "sd": 3.1},
            15: {"mean": 77.6, "sd": 3.0},
            16: {"mean": 78.2, "sd": 3.9}
        },
        "Female": {
            6: {"mean": 76.0, "sd": 3.5},
            7: {"mean": 76.3, "sd": 3.1},
            8: {"mean": 76.7, "sd": 3.3},
            9: {"mean": 76.5, "sd": 3.4},
            10: {"mean": 76.7, "sd": 3.5},
            11: {"mean": 77.3, "sd": 3.9},
            12: {"mean": 77.7, "sd": 3.4},
            13: {"mean": 77.5, "sd": 3.9},
            14: {"mean": 77.9, "sd": 3.8},
            15: {"mean": 78.9, "sd": 3.9},
            16: {"mean": 79.2, "sd": 2.3}
        }
    },

    # -------- Co-Go (mm) --------
    "Co-Go": {
        "Male": {
            6: {"mean": 48.7, "sd": 3.5},
            7: {"mean": 49.1, "sd": 3.4},
            8: {"mean": 51.3, "sd": 3.1},
            9: {"mean": 52.8, "sd": 3.3},
            10: {"mean": 54.0, "sd": 3.5},
            11: {"mean": 55.8, "sd": 3.5},
            12: {"mean": 57.2, "sd": 3.9},
            13: {"mean": 59.4, "sd": 4.2},
            14: {"mean": 61.6, "sd": 4.4},
            15: {"mean": 62.7, "sd": 4.1},
            16: {"mean": 66.1, "sd": 4.1}
        },
        "Female": {
            6: {"mean": 46.5, "sd": 2.9},
            7: {"mean": 47.7, "sd": 2.8},
            8: {"mean": 49.1, "sd": 2.9},
            9: {"mean": 50.8, "sd": 2.9},
            10: {"mean": 51.5, "sd": 2.7},
            11: {"mean": 52.4, "sd": 2.8},
            12: {"mean": 54.6, "sd": 3.9},
            13: {"mean": 55.1, "sd": 3.8},
            14: {"mean": 56.8, "sd": 3.5},
            15: {"mean": 58.9, "sd": 3.4},
            16: {"mean": 60.5, "sd": 2.4}
        }
    },

    # -------- Go-Pg (mm) --------
    "Go-Pg": {
        "Male": {
            6: {"mean": 66.1, "sd": 2.8},
            7: {"mean": 68.9, "sd": 3.0},
            8: {"mean": 71.2, "sd": 2.9},
            9: {"mean": 73.0, "sd": 2.7},
            10: {"mean": 75.1, "sd": 2.8},
            11: {"mean": 77.1, "sd": 3.2},
            12: {"mean": 78.5, "sd": 3.4},
            13: {"mean": 80.4, "sd": 3.7},
            14: {"mean": 82.8, "sd": 4.0},
            15: {"mean": 84.3, "sd": 4.1},
            16: {"mean": 86.5, "sd": 3.7}
        },
        "Female": {
            6: {"mean": 66.1, "sd": 4.2},
            7: {"mean": 67.9, "sd": 3.9},
            8: {"mean": 70.4, "sd": 4.2},
            9: {"mean": 71.7, "sd": 4.5},
            10: {"mean": 74.0, "sd": 4.2},
            11: {"mean": 75.7, "sd": 4.2},
            12: {"mean": 76.6, "sd": 3.8},
            13: {"mean": 78.4, "sd": 4.0},
            14: {"mean": 79.4, "sd": 3.7},
            15: {"mean": 80.6, "sd": 3.9},
            16: {"mean": 81.5, "sd": 3.8}
        }
    },

    # -------- Co-Pg (mm) --------
    "Co-Pg": {
        "Male": {
            6: {"mean": 101.8, "sd": 4.4},
            7: {"mean": 104.1, "sd": 3.5},
            8: {"mean": 107.8, "sd": 3.8},
            9: {"mean": 109.9, "sd": 4.0},
            10: {"mean": 112.8, "sd": 4.0},
            11: {"mean": 115.8, "sd": 4.5},
            12: {"mean": 117.9, "sd": 4.8},
            13: {"mean": 121.0, "sd": 5.5},
            14: {"mean": 124.1, "sd": 5.9},
            15: {"mean": 126.3, "sd": 5.1},
            16: {"mean": 130.9, "sd": 5.7}
        },
        "Female": {
            6: {"mean": 98.9, "sd": 4.3},
            7: {"mean": 101.6, "sd": 4.6},
            8: {"mean": 104.5, "sd": 5.0},
            9: {"mean": 106.7, "sd": 5.2},
            10: {"mean": 109.5, "sd": 4.9},
            11: {"mean": 111.6, "sd": 4.9},
            12: {"mean": 114.0, "sd": 4.6},
            13: {"mean": 116.1, "sd": 3.9},
            14: {"mean": 118.1, "sd": 3.9},
            15: {"mean": 120.1, "sd": 5.1},
            16: {"mean": 121.4, "sd": 3.9}
        }
    },

    # -------- ANS-Me (mm) --------
    "ANS-Me": {
        "Male": {
            6: {"mean": 63.7, "sd": 4.0},
            7: {"mean": 65.5, "sd": 4.4},
            8: {"mean": 66.6, "sd": 4.4},
            9: {"mean": 67.3, "sd": 4.3},
            10: {"mean": 68.9, "sd": 4.9},
            11: {"mean": 70.3, "sd": 4.8},
            12: {"mean": 71.1, "sd": 5.1},
            13: {"mean": 72.0, "sd": 5.6},
            14: {"mean": 74.3, "sd": 5.8},
            15: {"mean": 76.7, "sd": 6.4},
            16: {"mean": 79.5, "sd": 6.2}
        },
        "Female": {
            6: {"mean": 61.6, "sd": 3.9},
            7: {"mean": 63.6, "sd": 4.1},
            8: {"mean": 63.5, "sd": 4.2},
            9: {"mean": 64.1, "sd": 4.6},
            10: {"mean": 65.3, "sd": 4.9},
            11: {"mean": 65.8, "sd": 4.6},
            12: {"mean": 66.5, "sd": 3.8},
            13: {"mean": 68.1, "sd": 4.5},
            14: {"mean": 69.1, "sd": 5.0},
            15: {"mean": 69.5, "sd": 5.3},
            16: {"mean": 69.3, "sd": 5.2}
        }
    },

    # -------- ANS-PNS (mm) --------
    "ANS-PNS": {
        "Male": {
            6: {"mean": 50.2, "sd": 2.2},
            7: {"mean": 51.4, "sd": 2.5},
            8: {"mean": 52.1, "sd": 2.9},
            9: {"mean": 53.3, "sd": 2.9},
            10: {"mean": 54.4, "sd": 2.6},
            11: {"mean": 56.0, "sd": 2.4},
            12: {"mean": 56.7, "sd": 3.1},
            13: {"mean": 57.8, "sd": 3.0},
            14: {"mean": 58.7, "sd": 3.6},
            15: {"mean": 59.6, "sd": 3.6},
            16: {"mean": 61.6, "sd": 3.7}
        },
        "Female": {
            6: {"mean": 48.9, "sd": 2.3},
            7: {"mean": 50.5, "sd": 2.9},
            8: {"mean": 51.2, "sd": 2.5},
            9: {"mean": 51.2, "sd": 3.2},
            10: {"mean": 53.1, "sd": 3.1},
            11: {"mean": 53.9, "sd": 4.0},
            12: {"mean": 54.1, "sd": 3.2},
            13: {"mean": 55.3, "sd": 3.0},
            14: {"mean": 56.7, "sd": 2.9},
            15: {"mean": 57.1, "sd": 2.7},
            16: {"mean": 57.0, "sd": 4.4}
        }
    }
}
    
# Helper: linear interpolation between ages

def interpolate(param, sex, age):
    ages = sorted(growth_data[param][sex].keys())
    if age <= ages[0]:
        return growth_data[param][sex][ages[0]]
    if age >= ages[-1]:
        return growth_data[param][sex][ages[-1]]

    for i in range(len(ages) - 1):
        if ages[i] <= age <= ages[i + 1]:
            a1, a2 = ages[i], ages[i + 1]
            d1, d2 = growth_data[param][sex][a1], growth_data[param][sex][a2]
            ratio = (age - a1) / (a2 - a1)
            mean = d1["mean"] + ratio * (d2["mean"] - d1["mean"])
            sd = d1["sd"] + ratio * (d2["sd"] - d1["sd"])
            return {"mean": mean, "sd": sd}

# -----------------------------

# NOTE: Replace these with age- & sex-specific lookup tables later

growth_rates = {
    "FMA": -0.2,      # deg/year
    "SNB": 0.6,
    "Co-Go": 1.5,    # mm/year
    "Go-Pg": 2.0,
    "Co-Pg": 3.0,
    "ANS-Me": 2.2,
    "ANS-PNS": 1.6
}

# -----------------------------
# 5. COMPUTATION (Z-SCORE BASED)
# -----------------------------
results = []

age_start = age
age_end = min(age + duration_years, 16)  # growth capped at 16

for p in selected_params:
    if p not in growth_data or sex not in growth_data[p]:
        continue

    pre = input_data[p]["pre"]
    post = input_data[p]["post"]
    observed = post - pre

    ref_start = interpolate(p, sex, age_start)
    ref_end = interpolate(p, sex, age_end)

    # Z-score at baseline
    z = (pre - ref_start["mean"]) / ref_start["sd"] if ref_start["sd"] != 0 else 0

    # Predicted individual value at end
    predicted_end = ref_end["mean"] + z * ref_end["sd"]
    predicted_growth = predicted_end - pre

    treatment_effect = observed - predicted_growth

    results.append({
        "Parameter": p,
        "Pre": round(pre, 2),
        "Predicted Growth Δ": round(predicted_growth, 2),
        "Observed Δ": round(observed, 2),
        "Treatment Δ": round(treatment_effect, 2)
    })

# -----------------------------

results = []

for p in selected_params:
    pre = input_data[p]["pre"]
    post = input_data[p]["post"]
    observed = post - pre
    predicted_growth = growth_rates[p] * duration_years
    treatment_effect = observed - predicted_growth

    results.append({
        "Parameter": p,
        "Pre": round(pre, 2),
        "Predicted Growth Δ": round(predicted_growth, 2),
        "Observed Δ": round(observed, 2),
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
    st.info("Select parameters and enter values to see results.")

# -----------------------------
# 7. PDF GENERATION
# -----------------------------

def generate_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    pdf.cell(0, 10, "Growth-Adjusted Cephalometric Outcome Report", ln=True)
    pdf.ln(4)

    pdf.cell(0, 8, f"Age: {age} years", ln=True)
    pdf.cell(0, 8, f"Sex: {sex}", ln=True)
    pdf.cell(0, 8, f"Treatment duration: {round(duration_years,2)} years", ln=True)
    pdf.ln(5)

    for _, row in df.iterrows():
        line = f"{row['Parameter']}: Pre={row['Pre']} | GrowthΔ={row['Predicted Growth Δ']} | ObsΔ={row['Observed Δ']} | TreatΔ={row['Treatment Δ']}"
        pdf.multi_cell(0, 8, line)

    pdf.ln(4)
    pdf.multi_cell(0, 8, "Formula: Treatment Change = Observed Change − Predicted Growth Change")

    return pdf

if results:
    if st.button("Generate PDF"):
        pdf = generate_pdf(df)
        pdf_bytes = pdf.output(dest="S").encode("latin-1")
        st.download_button("Download PDF", pdf_bytes, file_name="cephalometric_report.pdf", mime="application/pdf")
