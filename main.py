import os
import json
import streamlit as st
import datetime
import math
from meldrx_fhir_client import FHIRClient

# Workspaces...
workspaceId_Smart = "02797a82-b390-4b99-846a-641ea6ef3c38"
workspaceId_Epic = "8c3aab4f-e90b-4c77-ae54-2c9c7319a134"
MELDRX_WORKSPACE_ID_DEFAULT = workspaceId_Epic

# Initial patient...
patientId_Smart = "5ee05359-57bf-4cee-8e89-91382c07e162"  # Barney Abbot
patientId_Epic = "eD.LxhDyX35TntF77l7etUA3" # Jason Argonaut
PATIENT_ID_DEFAULT = patientId_Epic

# Configuration...
MELDRX_CLIENT_SECRET = os.environ.get("MELDRX_CLIENT_SECRET")
MELDRX_BASE_URL = "https://app.meldrx.com"
MELDRX_CLIENT_ID = "46eaeaab5c03422986c9bd1157182643"
SCOPE = "system/*.read"

def get_fhir_client(useEpic):
    # Choose the workspace...
    workspace_id = workspaceId_Smart
    if (useEpic):
        workspace_id = workspaceId_Epic

    return FHIRClient.for_client_secret(MELDRX_BASE_URL, workspace_id, MELDRX_CLIENT_ID, MELDRX_CLIENT_SECRET, SCOPE)

# Calculate the Cambridge Diabetes Risk Score...
def calculate_cambridge_diabetes_risk_score(gender, prescribed_anti_hypertensive, prescribed_steroids, age, bmi, relatives_with_diabetes, smoke_status):
    a = -6.322
    B1 = 0 if gender == "male" else -0.879
    B2 = 1.222 if prescribed_anti_hypertensive else 0
    B3 = 2.191 if prescribed_steroids else 0
    B4 = 0.063 * age

    B5 = 0
    if 25 <= bmi < 27.5:
        B5 = 0.699
    elif 27.5 <= bmi < 30:
        B5 = 1.97
    elif bmi >= 30:
        B5 = 2.518

    B6 = 0
    if relatives_with_diabetes == "parentOrSibling":
        B6 = 0.728
    elif relatives_with_diabetes == "parentAndSibling":
        B6 = 0.753

    B7 = 0
    if smoke_status == "past":
        B7 = -0.218
    elif smoke_status == "current":
        B7 = 0.855

    sum = a + B1 + B2 + B3 + B4 + B5 + B6 + B7
    score = 1 / (1 + math.exp(-sum))
    return score

# Search for patients by name/dob...
def search_patients(first_name, last_name, dob, use_epic):
    fhirClient = get_fhir_client(use_epic)

    # Format inputs...
    # TODO: Until date_input allows a blank value, I am just using text for the DOB
    #sDob = ""
    #if (dob != None):
    #    sDob = dob.strftime("%Y-%m-%d")
    sDob = dob

    search_params = { }
    if (first_name != ""):
        search_params["given"] = first_name
    if (last_name != ""):
        search_params["family"] = last_name
    if (sDob != ""):
        search_params["birthdate"] = sDob

    # Search patients...
    searchResults = fhirClient.search_resource("Patient", search_params)
    return searchResults

def render():
    # Start off with a random patient for demonstration purposes...
    if ('isInitialized' not in st.session_state):
        fhirClient = get_fhir_client(MELDRX_WORKSPACE_ID_DEFAULT == workspaceId_Epic)
        patient = fhirClient.read_resource("Patient", PATIENT_ID_DEFAULT)

        patientId = patient["id"]
        patientName = patient["name"][0]["given"][0] + " " + patient["name"][0]["family"]
        patientGender = patient["gender"]
        patientDOB = patient["birthDate"]
        patientAge = datetime.datetime.now().year - int(patientDOB[0:4])

        # Add all to session state...
        st.session_state['patient'] = patient
        st.session_state['patientId'] = patientId
        st.session_state['patientName'] = patientName
        st.session_state['patientGender'] = patientGender
        st.session_state['patientDOB'] = patientDOB
        st.session_state['patientAge'] = patientAge
        st.session_state['isInitialized'] = True

    # If patient is in the session, load it into the variables...
    if ('patient' in st.session_state):
        patient = st.session_state['patient']
        patientId = st.session_state['patientId']
        patientName = st.session_state['patientName']
        patientGender = st.session_state['patientGender']
        patientDOB = st.session_state['patientDOB']
        patientAge = st.session_state['patientAge']

    # App Header...
    st.title("Cambridge Diabetes Risk Score")
    st.markdown("[https://www.mdcalc.com/cambridge-diabetes-risk-score](%s)" % "https://www.mdcalc.com/cambridge-diabetes-risk-score")
    st.markdown("This tool calculates the risk of undiagnosed diabetes in patients based on the Cambridge Diabetes Risk Score.")
    st.markdown("Please search for a patient, then update their risk factors as needed. Click 'Calculate' to see the results.")
    st.markdown("___")

    # Search for Patient (first name, last name, birthdate)...
    st.markdown("## Search for Patient")
    useEpic = st.checkbox("Check here to use Epic. Otherwise, it will use another EHR", value=True)
    searchFirstName = st.text_input("First Name")
    searchLastName = st.text_input("Last Name")
    searchDOB = st.text_input("Date of Birth (YYYY-MM-DD)")
    #searchDOB = st.date_input("Date of Birth", None, min_value=datetime.datetime(1900, 1, 1), max_value=datetime.datetime.now())
    if st.button("Search"):
        searchResults = search_patients(searchFirstName, searchLastName, searchDOB, useEpic)

        # If no entries, display message and return...
        if (not "entry" in searchResults):
            st.markdown("No patients found.")
            return

        # Look at bundle and just take the first result...
        entry = searchResults["entry"][0]
        if (entry == None):
            st.markdown("No patients found.")
            return

        # Grab data about the patient...
        patient = entry["resource"]
        patientId = patient["id"]
        patientName = patient["name"][0]["given"][0] + " " + patient["name"][0]["family"]
        patientGender = patient["gender"]
        patientDOB = patient["birthDate"]
        patientAge = datetime.datetime.now().year - int(patientDOB[0:4])

        # Save to session state...
        st.session_state['patient'] = patient
        st.session_state['patientId'] = patientId
        st.session_state['patientName'] = patientName
        st.session_state['patientGender'] = patientGender
        st.session_state['patientDOB'] = patientDOB
        st.session_state['patientAge'] = patientAge
    st.markdown("___")

    # Patient Information...
    if (patient != None):
        st.markdown("## Patient Data")
        st.markdown("Name: " + patientName)
        st.markdown("Gender: " + patientGender)
        st.markdown("Age: " + str(patientAge))
        st.markdown("___")

    # Input fields, initialized with patient data (if possible)...
    st.markdown("## Risk Factors")
    gender = st.selectbox("Gender", ("Male", "Female"), 1 if patientGender == "female" else 0)
    prescribed_anti_hypertensive_meds = st.checkbox("Prescribed Anti-hypertensive Medications")
    prescribed_steroids = st.checkbox("Prescribed Steroids")
    age = st.number_input("Age (years)", min_value=0, max_value=150, value=patientAge, step=1)
    bmi = st.number_input("BMI (kg/m^2)", min_value=10.0, max_value=100.0, value=25.0, step=0.1)
    relatives_with_diabetes = st.selectbox("Relatives with Diabetes", ("None", "Parent or Sibling", "Parent and Sibling"))
    smoking_history = st.selectbox("Smoking History", ("Never", "Past", "Current"))

    # Calculate button and results...
    if st.button("Calculate"):
        result = calculate_cambridge_diabetes_risk_score(gender, prescribed_anti_hypertensive_meds, prescribed_steroids, age, bmi, relatives_with_diabetes, smoking_history)
        st.markdown("## Results")
        st.write(f"Score: {result:.2f} %")
        st.write(f"This patient has a {result:.2f}% chance of having undiagnosed diabetes.")

render()