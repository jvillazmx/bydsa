import streamlit as st
import os

st.title("Cuenta de servicio activa")
st.write("Esta es la cuenta con la que se ejecuta el entorno de Streamlit:")
st.code(os.environ.get("GOOGLE_SERVICE_ACCOUNT_EMAIL", "No definida"))
