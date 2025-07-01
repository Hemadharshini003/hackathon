import tkinter as tk
from tkinter import ttk, messagebox
import speech_recognition as sr
import pandas as pd
import spacy

# For translation
try:
    from deep_translator import GoogleTranslator
except ImportError:
    raise ImportError("Please install deep-translator using: pip install deep-translator")

# Load English NLP model
nlp = spacy.load("en_core_web_sm")

# Initialize translator
translator = GoogleTranslator(source='auto', target='en')

# Catalog setup
catalog_file = "voice_catalog.csv"
try:
    catalog = pd.read_csv(catalog_file)
except:
    catalog = pd.DataFrame(columns=["Product", "Quantity", "Price"])

# NLP extraction
def extract_info(text):
    doc = nlp(text)
    product = None
    quantity = None
    price = None

    for token in doc:
        if token.like_num and quantity is None:
            quantity = token.text
        elif token.text.lower() in ["kg", "litre", "l", "pack", "units"]:
            quantity += f" {token.text}"
        elif "₹" in token.text or "rs" in token.text.lower():
            price = token.text
        elif token.pos_ == "NOUN" and product is None:
            product = token.text
    return product, quantity, price

# Speech recognition with language selection
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        status_label.config(text="🎙️ Listening...")
        app.update()
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            status_label.config(text="❌listening time out.")
            return None

    lang = language_var.get()
    try:
        # Recognize speech based on selected language
        lang_code = "ta-IN" if lang == "Tamil" else "en-IN"
        text = recognizer.recognize_google(audio, language=lang_code)
        if lang != "English":
            text = translator.translate(text)
        status_label.config(text=f"📝 Recognized: {text}")
        return text
    except Exception as e:
        status_label.config(text=f"❌ Recognition failed.")
        print(e)
        return None

# Add product logic
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
            messagebox.showinfo("Success", "Product added to catalog.")
        else:
            messagebox.showwarning("Error", "Could not extract product info.")

# Refresh table
def refresh_table():
    for row in table.get_children():
        table.delete(row)
    for _, row in catalog.iterrows():
        table.insert("", tk.END, values=list(row))

# GUI setup
app = tk.Tk()
app.title("Multilingual Voice Catalog Agent")
app.geometry("630x450")

tk.Label(app, text="Voice Catalog System", font=("Arial", 16)).pack(pady=10)

tk.Label(app, text="Choose Language:").pack()
language_var = tk.StringVar(value="English")
language_selector = ttk.Combobox(app, textvariable=language_var, values=["English", "Tamil"], state="readonly")
language_selector.pack()

tk.Button(app, text="🎤 Add Product by Voice", command=add_product, font=("Arial", 12), bg="#4CAF50", fg="white").pack(pady=10)

status_label = tk.Label(app, text="Status: Waiting...", fg="blue")
status_label.pack()

table = ttk.Treeview(app, columns=["Product", "Quantity", "Price"], show="headings")
for col in ["Product", "Quantity", "Price"]:
    table.heading(col, text=col)
table.pack(expand=True, fill="both", padx=10, pady=10)

refresh_table()
app.mainloop()
