import streamlit as st
import datetime
from meldrx_fhir_client import FHIRClient

#client = meldrx_fhir_client.FHIRClient.for_no_auth("http://google")
#print(client)

fhirUrl = "https://launch.smarthealthit.org/v/r4/sim/WzMsIiIsIiIsIkFVVE8iLDAsMCwwLCIiLCIiLCIiLCIiLCIiLCIiLCIiLDAsMV0/fhir"
patientId = "5ee05359-57bf-4cee-8e89-91382c07e162"

def calculate(gender, prescribed_anti_hypertensive_meds, prescribed_steroids, age, bmi, relatives_with_diabetes, smoking_history):
    return 13.67

def render():
    fhirClient = FHIRClient.for_no_auth(fhirUrl)

    # Query patient demographics...
    patient = fhirClient.read_resource("Patient", patientId)
    print(patient)
    patientName = patient["name"][0]["given"][0] + " " + patient["name"][0]["family"]
    patientGender = patient["gender"]
    patientDOB = patient["birthDate"]
    patientAge = datetime.datetime.now().year - int(patientDOB[0:4])

    # App Header...
    st.title("Cambridge Diabetes Risk Score")
    st.markdown("[https://www.mdcalc.com/cambridge-diabetes-risk-score](%s)" % "https://www.mdcalc.com/cambridge-diabetes-risk-score")

    # Patient Information...
    st.markdown("**Patient Data:**")
    st.markdown("Name: " + patientName)
    st.markdown("Gender: " + patientGender)
    st.markdown("Age: " + str(patientAge))
    st.markdown("___")

    # Input fields, initialized with patient data (if possible)...
    gender = st.selectbox("Gender", ("Male", "Female"), 1 if patientGender == "female" else 0)
    prescribed_anti_hypertensive_meds = st.checkbox("Prescribed Anti-hypertensive Medications")
    prescribed_steroids = st.checkbox("Prescribed Steroids")
    age = st.number_input("Age (years)", min_value=1, max_value=150, value=patientAge, step=1)
    bmi = st.number_input("BMI (kg/m^2)", min_value=10.0, max_value=100.0, value=25.0, step=0.1)
    relatives_with_diabetes = st.selectbox("Relatives with Diabetes", ("None", "Parent or Sibling", "Parent and Sibling"))
    smoking_history = st.selectbox("Smoking History", ("Never", "Past", "Current"))

    if st.button("Calculate"):
        result = calculate(gender, prescribed_anti_hypertensive_meds, prescribed_steroids, age, bmi, relatives_with_diabetes, smoking_history)
        st.write(f"Score: {result:.2f} %")

render()