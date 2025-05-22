import streamlit as st
import pandas as pd
import random
import requests
from datetime import date
import os

st.set_page_config(page_title="Evaluación interna BYDSA", layout="centered")

# Web App URL actualizada
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyvOmFmYuIn_V8E2jwOBEEoLq-VduuSgjj_Y-LYDLldjTRwi7z2-6uei6ikDggKjTJOmw/exec"

# Archivos CSV por categoría
archivos = [
    "adaptacion.csv", "colaboracion.csv", "compromiso.csv", "cumplimiento.csv",
    "estrategia.csv", "impacto.csv", "mejora.csv", "resiliencia.csv"
]

# Ruta a la carpeta 'csv'
csv_dir = os.path.join(os.getcwd(), "csv")

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

# Mostrar formulario solo si no se ha enviado aún
if "evaluacion_enviada" not in st.session_state:

    st.title("📋 Evaluación interna BYDSA")
    st.subheader("Instrucción")
    st.write("Usa una escala del 1 (nunca) al 5 (siempre) para calificar cada afirmación.")

    if "preguntas" not in st.session_state:
        st.session_state.preguntas = cargar_preguntas()

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

    if enviado:
        if not evaluador or not evaluado:
            st.warning("⚠️ Debes completar el nombre del evaluador y evaluado.")
        elif any(v is None for v in respuestas.values()):
            st.warning("⚠️ Debes contestar todas las preguntas antes de enviar.")
        else:
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

            try:
                r = requests.post(WEB_APP_URL, json=datos)
                if r.status_code == 200 and "OK" in r.text:
                    st.session_state.evaluacion_enviada = True
                else:
                    st.warning("⚠️ El servidor respondió con error.")
            except Exception as e:
                st.error(f"🚫 No se pudo conectar con el servidor: {e}")

# Mostrar pantalla final tras envío
if st.session_state.get("evaluacion_enviada"):
    st.success("✅ Evaluación enviada exitosamente.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Otra evaluación"):
            st.session_state.clear()
            st.experimental_rerun()

    with col2:
        if st.button("🚪 Cerrar"):
            st.markdown("Gracias por participar. Puedes cerrar esta pestaña.")
            st.stop()
