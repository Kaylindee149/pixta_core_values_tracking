import json

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

EMPLOYEE_SHEET = 'General Info'
ANSWER_SHEET = 'Answers'
REDEEM_HISTORY_SHEET = 'Redeemed ticket'


def read_private_google_sheet(sheet_url: str, sheet_name: str):
    # Define the scope
    scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    service_account_info = json.loads(st.secrets["google_service_account"]["JSON_KEY"])
    # Create credentials using the service account key file
    credentials = Credentials.from_service_account_info(service_account_info, scopes=scopes)

    # Authorize the client
    gc = gspread.authorize(credentials)

    # Open the Google Sheet by URL
    sh = gc.open_by_url(sheet_url)

    # Get the worksheet by name
    worksheet = sh.worksheet(sheet_name)

    # Get all values in the worksheet
    data = worksheet.get_all_values()

    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(data[1:], columns=data[0])  # Skip the header row in data[0] if necessary

    return df


@st.cache_resource(show_spinner=False, ttl=300)
def get_employees() -> dict:
    df = read_private_google_sheet(st.secrets.DATABASE_URL, EMPLOYEE_SHEET)
    df_indexed = df.set_index('Email')
    return df_indexed.to_dict(orient='index')


@st.cache_resource(show_spinner=False, ttl=300)
def get_answers() -> pd.DataFrame:
    return read_private_google_sheet(st.secrets.DATABASE_URL, ANSWER_SHEET)


@st.cache_resource(show_spinner=False, ttl=300)
def get_redeem_history() -> pd.DataFrame:
    return read_private_google_sheet(st.secrets.DATABASE_URL, REDEEM_HISTORY_SHEET)


def get_all_data() -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    employees = get_employees()
    answers = get_answers()
    redeem_history = get_redeem_history()
    return employees, answers, redeem_history


def verify_user(email: str, password: str) -> bool:
    employees = get_employees()
    return email in employees and employees[email]['Password'] == password


def get_info_by_email(email) -> dict:
    """
    Get the information of an employee by email
    :param email:
    :return: general information and answers of the employee
    """
    employees = get_employees()
    answers = get_answers()
    redeem_history = get_redeem_history()
    filtered_answers = answers[answers['Email'] == email]
    filtered_history = redeem_history[redeem_history['Email'] == email]
    list_of_answers = filtered_answers.to_dict(orient='records')
    list_of_history = filtered_history.to_dict(orient='records')
    return {'general_info': employees[email], 'answers': list_of_answers, 'history': list_of_history}
