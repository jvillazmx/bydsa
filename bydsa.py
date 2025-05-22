import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import random
import os
import requests
import json
from datetime import date

# Ruta base donde están los CSV
csv_dir = r"C:\Users\jvill\Documents\BYDSA\Evaluacion\csv"

# Archivos CSV
archivos = [
    "adaptacion.csv", "colaboracion.csv", "compromiso.csv", "cumplimiento.csv",
    "estrategia.csv", "impacto.csv", "mejora.csv", "resiliencia.csv"
]

# URL del Web App de Google Apps Script
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbw0Flcbt4T_-C72kL_C8SqAdxQRjbauVumHxNPJxIUZC3tcdTh-v6CGOVp7rIPAlh6htA/exec"

def cargar_preguntas():
    preguntas = []
    for archivo in archivos:
        path = os.path.join(csv_dir, archivo)
        if not os.path.exists(path):
            print(f"❌ Archivo no encontrado: {archivo}")
            continue

        try:
            df = pd.read_csv(path, encoding="latin1")
            df = df[df["PREGUNTA"].notna()]
            df = df[df["PREGUNTA"].str.strip() != ""]
            if len(df) >= 3:
                df_sampled = df.sample(n=3, random_state=random.randint(1, 9999)).reset_index(drop=True)
                categoria = os.path.splitext(archivo)[0].capitalize()
                for _, row in df_sampled.iterrows():
                    preguntas.append((categoria, row["NUMERO"], row["PREGUNTA"]))
            else:
                print(f"⚠️ El archivo {archivo} no tiene suficientes preguntas válidas.")
        except Exception as e:
            print(f"⚠️ Error al leer {archivo}: {e}")
    return preguntas

def iniciar_gui():
    global root, entry_evaluador, entry_evaluado, entry_fecha, respuestas, preguntas_seleccionadas, canvas, scrollable_frame

    preguntas_seleccionadas = cargar_preguntas()
    if not preguntas_seleccionadas:
        raise RuntimeError("No se cargaron preguntas. Verifica los archivos CSV.")

    root = tk.Tk()
    root.title("Evaluación de Comportamientos")
    root.geometry("900x800")

    canvas = tk.Canvas(root)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    ttk.Label(scrollable_frame, text="Evaluación de Comportamientos", font=("Arial", 16, "bold")).pack(pady=10)
    entry_frame = ttk.Frame(scrollable_frame)
    entry_frame.pack(pady=5)

    ttk.Label(entry_frame, text="Persona que hace la evaluación:").grid(row=0, column=0, sticky="w")
    entry_evaluador = ttk.Entry(entry_frame, width=40)
    entry_evaluador.grid(row=0, column=1)

    ttk.Label(entry_frame, text="Persona evaluada:").grid(row=1, column=0, sticky="w")
    entry_evaluado = ttk.Entry(entry_frame, width=40)
    entry_evaluado.grid(row=1, column=1)

    ttk.Label(entry_frame, text="Fecha de evaluación:").grid(row=2, column=0, sticky="w")
    entry_fecha = ttk.Entry(entry_frame, width=40)
    entry_fecha.insert(0, str(date.today()))
    entry_fecha.grid(row=2, column=1)

    instrucciones = (
        "Instrucciones: Por favor responda a cada pregunta en el número que mejor represente a la persona evaluada,\n"
        "donde '1' indica que la persona nunca o casi nunca muestra ese comportamiento y '5' indica que la persona\n"
        "siempre o casi siempre muestra ese comportamiento.\n\n"
        "La persona evaluada no recibirá el detalle del nombre o nombres de quienes la han evaluado,\n"
        "solo un resumen general de sus resultados."
    )
    ttk.Label(scrollable_frame, text=instrucciones, justify="left", wraplength=800).pack(pady=10)

    respuestas = {}

    for idx, (categoria, numero, pregunta) in enumerate(preguntas_seleccionadas, 1):
        frame = ttk.LabelFrame(scrollable_frame, text=f"{idx}. {categoria}", padding=10)
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame, text=pregunta, wraplength=750, justify="left").pack(anchor="w")
        var = tk.IntVar(value=0)
        respuestas[f"{categoria}_{numero}"] = {"var": var, "pregunta": pregunta}

        for i in range(1, 6):
            ttk.Radiobutton(frame, text=str(i), variable=var, value=i).pack(side="left", padx=5)

    ttk.Button(scrollable_frame, text="Terminar evaluación", command=lambda: terminar(respuestas)).pack(pady=20)

def terminar(respuestas):
    evaluador = entry_evaluador.get()
    evaluado = entry_evaluado.get()
    fecha_eval = entry_fecha.get()

    if not evaluador or not evaluado:
        messagebox.showwarning("Campos faltantes", "Por favor, complete los campos de evaluador y evaluado.")
        return

    for val in respuestas.values():
        if val["var"].get() == 0:
            messagebox.showwarning("Preguntas incompletas", "Por favor, conteste todas las preguntas antes de continuar.")
            return

    data = []
    for key, val in respuestas.items():
        categoria, numero = key.split("_", 1)
        data.append({
            "fecha": fecha_eval,
            "evaluador": evaluador,
            "evaluado": evaluado,
            "categoria": categoria,
            "pregunta": val["pregunta"],
            "numero": numero,
            "valor": val["var"].get()
        })

    try:
        response = requests.post(WEB_APP_URL, json=data)
        if response.status_code == 200 and response.text.strip() == "OK":
            mostrar_resultado()
        else:
            messagebox.showerror("Error", f"Fallo al enviar datos: {response.text}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar: {e}")

def mostrar_resultado():
    resultado = tk.Toplevel(root)
    resultado.title("Evaluación completada")
    resultado.geometry("400x200")
    ttk.Label(resultado, text="Evaluación enviada con éxito.\n¿Qué desea hacer a continuación?", justify="center").pack(pady=20)

    def cerrar_todo():
        root.destroy()
        resultado.destroy()

    def reiniciar():
        resultado.destroy()
        root.destroy()
        iniciar_gui()

    boton_frame = ttk.Frame(resultado)
    boton_frame.pack(pady=10)
    ttk.Button(boton_frame, text="Otra evaluación", command=reiniciar).pack(side="left", padx=10)
    ttk.Button(boton_frame, text="Cerrar", command=cerrar_todo).pack(side="right", padx=10)

# Ejecutar GUI
iniciar_gui()
root.mainloop()
