import tkinter as tk
from tkinter import ttk, messagebox
import speech_recognition as sr
import pandas as pd
import spacy

# Load NLP model
nlp =spacy.load("en_core_web_sm")

# Catalog storage
catalog_file = "voice_catalog.csv"

try:
    catalog = pd.read_csv(catalog_file)
except:
    catalog = pd.DataFrame(columns=["Product", "Quantity", "Price"])

# Extract info using spaCy
def extract_info(text):
    doc = nlp(text)
    product = None
    quantity = None
    price = None

    for token in doc:
        if token.like_num and quantity is None:
            quantity = token.text
        if token.text.lower() in ["kg", "litre", "l", "pack", "units"]:
            quantity += f" {token.text}"
        if "₹" in token.text or "rs" in token.text.lower():
            price = token.text
        if token.pos_ == "NOUN" and product is None:
            product = token.text
    return product, quantity, price

# Recognize speech
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        status_label.config(text="🎙️ Listening...")
        app.update()
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        status_label.config(text=f"📝 Recognized: {text}")
        return text
    except:
        status_label.config(text="❌ Could not recognize speech.")
        return None

# Add product to catalog
def add_product():
    text = recognize_speech()
    if text:
        product, quantity, price = extract_info(text)
        if product and quantity and price:
            global catalog
            new_row = pd.DataFrame([[product, quantity, price]], columns=["Product", "Quantity", "Price"])
            catalog = pd.concat([catalog, new_row], ignore_index=True)
            catalog.to_csv(catalog_file, index=False)
            refresh_table()
            messagebox.showinfo("Success", "Product added to catalog!")
        else:
            messagebox.showwarning("Error", "Could not extract product info.")

# Refresh table display
def refresh_table():
    for row in table.get_children():
        table.delete(row)
    for _, row in catalog.iterrows():
        table.insert("", tk.END, values=list(row))

# Tkinter GUI
app = tk.Tk()
app.title("Voice-to-Catalog Agent")
app.geometry("600x400")

tk.Label(app, text="AI-Powered Voice Catalog System", font=("Arial", 16)).pack(pady=10)

record_btn = tk.Button(app, text="🎤 Add Product via Voice", command=add_product, bg="#4CAF50", fg="white", font=("Arial", 12))
record_btn.pack(pady=10)

status_label = tk.Label(app, text="Status: Waiting...", fg="blue")
status_label.pack()

# Table
table = ttk.Treeview(app, columns=["Product", "Quantity", "Price"], show="headings")
table.heading("Product", text="Product")
table.heading("Quantity", text="Quantity")
table.heading("Price", text="Price")
table.pack(expand=True, fill="both", padx=10, pady=10)

refresh_table()

app.mainloop()

