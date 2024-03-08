import streamlit as st
import meldrx_fhir_client

client = meldrx_fhir_client.FHIRClient.for_no_auth("http://google")
print(client)

def calculate(gender, prescribed_anti_hypertensive_meds, prescribed_steroids, age, bmi, relatives_with_diabetes, smoking_history):
    return 13.67

def render():

    st.title("Cambridge Diabetes Risk Score")
    st.markdown("[https://www.mdcalc.com/cambridge-diabetes-risk-score](%s)" % "https://www.mdcalc.com/cambridge-diabetes-risk-score")

    st.write("Patient Data:")
    # TODO: Add patient data

    gender = st.selectbox("Gender", ("Male", "Female"))
    prescribed_anti_hypertensive_meds = st.checkbox("Prescribed Anti-hypertensive Medications")
    prescribed_steroids = st.checkbox("Prescribed Steroids")
    age = st.number_input("Age (years)", min_value=1, max_value=150, value=50, step=1)
    bmi = st.number_input("BMI (kg/m^2)", min_value=10.0, max_value=100.0, value=25.0, step=0.1)
    relatives_with_diabetes = st.selectbox("Relatives with Diabetes", ("None", "Parent or Sibling", "Parent and Sibling"))
    smoking_history = st.selectbox("Smoking History", ("Never", "Past", "Current"))

    if st.button("Calculate"):
        result = calculate(gender, prescribed_anti_hypertensive_meds, prescribed_steroids, age, bmi, relatives_with_diabetes, smoking_history)
        st.write(f"Score: {result:.2f} %")

render()