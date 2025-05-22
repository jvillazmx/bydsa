import gspread
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
import streamlit as st

try:
    sa = gspread.service_account()
    sh = sa.open_by_key("1JiJttb7OfQIDAVlSCsymZP2r1bn7BOOnVLL89mYo2aY")
    st.success("¡Acceso exitoso!")
except Exception as e:
    st.error(f"ERROR al intentar acceder: {e}")

