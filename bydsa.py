import streamlit as st
import pandas as pd
import random
import requests
from datetime import date
import os

st.set_page_config(page_title="Evaluación interna BYDSA", layout="centered")

st.title("📋 Evaluación interna BYDSA")
st.subheader("Instrucción")
st.write("Usa una escala del 1 (nunca) al 5 (siempre) para calificar cada afirmación.")

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
                        "numero": str(row["NUMERO"]),
                        "pregunta": row["PREGUNTA"]
                    })
    return preguntas

# Cargar preguntas solo una vez
if "preguntas" not in st.session_state:
    st.session_state.preguntas = cargar_preguntas()

# Formulario
with st.form("formulario_evaluacion"):
    col1, col2 = st.columns(2)
    with col1:
        evaluador = st.text_input("👤 Persona que evalúa")
    with col2:
        evaluado = st.text_input("👥 Persona evaluada")
    fecha_eval = st.date_input("📅 Fecha de evaluación", value=date.today())

    st.markdown("---")
    st.markdown("### Responde a cada afirmación:")

    respuestas = {}

    for i, item in enumerate(st.session_state.preguntas, 1):
        st.markdown(f"**{i}. {item['categoria']}**")
        st.write(item["pregunta"])
        key = f"{item['categoria']}_{item['numero']}"
        respuestas[key] = st.radio(
            label="Selecciona un valor:",
            options=[1, 2, 3, 4, 5],
            index=None,
            key=f"radio_{key}",
            horizontal=True
        )

    enviado = st.form_submit_button("Enviar evaluación")

# Procesar envío
if enviado:
    st.write("🛠 Paso 1: Se presionó el botón de envío")

    if not evaluador or not evaluado:
        st.write("🛠 Paso 2: Validación de campos vacíos falló")
        st.warning("Debes completar el nombre del evaluador y evaluado.")
    elif any(v is None for v in respuestas.values()):
        st.write("🛠 Paso 3: Validación de respuestas incompletas falló")
        st.warning("Debes contestar todas las preguntas antes de enviar.")
    else:
        st.write("🛠 Paso 4: Validaciones pasadas. Preparando datos")

        datos = []
        for key, valor in respuestas.items():
            categoria, numero = key.split("_", 1)
            pregunta_texto = next(
                (p["pregunta"] for p in st.session_state.preguntas
                 if p["categoria"] == categoria and p["numero"] == numero),
                ""
            )
            datos.append({
                "fecha": str(fecha_eval),
                "evaluador": evaluador,
                "evaluado": evaluado,
                "categoria": categoria,
                "pregunta": pregunta_texto,
                "numero": numero,
                "valor": valor
            })

        st.write("🛠 Paso 5: Datos preparados para envío")
        st.json(datos)  # Visualiza el JSON enviado

try:
    r = requests.post(WEB_APP_URL, json=datos)
    st.write("🛠 Paso 6: POST enviado, analizando respuesta...")

    if r.status_code == 200 and "OK" in r.text:
        st.write("🛠 Paso 7: Respuesta recibida satisfactoriamente")
        st.success("✅ Evaluación enviada exitosamente.")
        st.session_state.pop("preguntas")
    else:
        st.write("🛠 Paso 8: Error en respuesta del servidor")
        st.text("Respuesta cruda del servidor:")
        st.text(r.text)
        st.warning("❌ Error al enviar los datos.")
except Exception as e:
    st.write("🛠 Paso 9: Error de conexión")
    st.text(f"Excepción: {e}")

