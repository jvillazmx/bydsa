import streamlit as st
import gspread

st.title("🔒 Prueba de acceso a Google Sheet")

try:
    # Intentar conectar con la hoja de cálculo por ID
    gc = gspread.service_account()
    sh = gc.open_by_key("1JiJttb7OfQIDAVlSCsymZP2r1bn7BOOnVLL89mYo2aY")
    worksheet = sh.sheet1
    st.success("✅ ¡Acceso exitoso a la hoja 'bydsa'!")
    st.write("Primeras 3 filas de la hoja:")
    rows = worksheet.get_all_values()
    st.dataframe(rows[:3])

except Exception as e:
    st.error("❌ No se pudo acceder a la hoja de cálculo.")
    st.code(str(e))
