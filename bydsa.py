import streamlit as st
import pandas as pd
import random
import requests
from datetime import date
import os

st.set_page_config(page_title="Evaluación BYDSA", layout="centered")

st.title("🧭 Evaluación de Comportamientos - BYDSA")

# Ruta a la carpeta 'csv'
csv_dir = os.path.join(os.getcwd(), "csv")

# Archivos CSV por categoría
archivos = [
    "adaptacion.csv", "colaboracion.csv", "compromiso.csv", "cumplimiento.csv",
    "estrategia.csv", "impacto.csv", "mejora.csv", "resiliencia.csv"
]

# URL de tu Web App en Google Apps Script
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbw0Flcbt4T_-C72kL_C8SqAdxQRjbauVumHxNPJxIUZC3tcdTh-v6CGOVp7rIPAlh6htA/exec"

# Función para cargar preguntas
def cargar_preguntas():
    preguntas = []
    for archivo in archivos:
        path = os.path.join(csv_dir, archivo)
        if os.path.exists(path):
            df = pd.read_csv(path, encoding="latin1")
            df = df[df["PREGUNTA"].notna()]
            df = df[df["PREGUNTA"].str.strip() != ""]
            if len(df) >= 3:
                categoria = os.path.splitext(archivo)[0].capitalize()
                seleccionadas = df.sample(n=3, random_state=random.randint(1, 9999)).reset_index(drop=True)
                for _, row in seleccionadas.iterrows():
                    preguntas.append({
                        "categoria": categoria,
                        "numero": row["NUMERO"],
                        "pregunta": row["PREGUNTA"]
                    })
    return preguntas

# Formulario de cabecera
with st.form("formulario_evaluacion"):
    col1, col2 = st.columns(2)
    with col1:
        evaluador = st.text_input("👤 Persona que evalúa")
    with col2:
        evaluado = st.text_input("👥 Persona evaluada")
    fecha_eval = st.date_input("📅 Fecha de evaluación", value=date.today())

    st.markdown("---")

    st.markdown("### Responde a cada afirmación según tu percepción del evaluado:")

    preguntas = cargar_preguntas()
    respuestas = {}

    for i, item in enumerate(preguntas, 1):
        st.markdown(f"**{i}. {item['categoria']}**")
        st.write(item["pregunta"])
        key = f"{item['categoria']}_{item['numero']}"
        respuestas[key] = st.radio(
            label="Selecciona un valor (1 = nunca, 5 = siempre)",
            options=[1, 2, 3, 4, 5],
            index=None,
            key=key,
            horizontal=True
        )

    enviado = st.form_submit_button("Enviar evaluación")

# Envío al Web App si se presiona el botón
if enviado:
    if not evaluador or not evaluado:
        st.warning("⚠️ Debes completar el nombre del evaluador y evaluado.")
    elif any(r is None for r in respuestas.values()):
        st.warning("⚠️ Debes contestar todas las preguntas antes de enviar.")
    else:
        datos = []
        for key, valor in respuestas.items():
            categoria, numero = key.split("_", 1)
            pregunta_texto = next((p["pregunta"] for p in preguntas if p["categoria"] == categoria and str(p["numero"]) == numero), "")
            datos.append({
                "fecha": str(fecha_eval),
                "evaluador": evaluador,
                "evaluado": evaluado,
                "categoria": categoria,
                "pregunta": pregunta_texto,
                "numero": numero,
                "valor": valor
            })

        try:
            r = requests.post(WEB_APP_URL, json=datos)
            if r.status_code == 200 and "OK" in r.text:
                st.success("✅ Evaluación enviada exitosamente.")
            else:
                st.error(f"❌ Error al enviar los datos: {r.text}")
        except Exception as e:
            st.error(f"🚫 No se pudo conectar con el servidor: {e}")
