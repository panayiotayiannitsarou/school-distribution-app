
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Κατανομή Μαθητών", layout="centered")
st.title("📘 Εφαρμογή Κατανομής Μαθητών")

# Προσθήκη κουμπιού για λήψη πρότυπου Excel
with open("Πρότυπο_Κατανομής_ΚΕΝΟ.xlsx", "rb") as f:
    st.download_button("📥 Κατέβασε το Πρότυπο Excel", f, file_name="Πρότυπο_Κατανομής.xlsx")

uploaded_file = st.file_uploader("Ανέβασε αρχείο Excel με μαθητές", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    required_columns = [
        "Όνομα", "Φύλο", "Παιδί Εκπαιδευτικού", "Ζωηρός",
        "Ιδιαιτερότητα", "Καλή γνώση Ελληνικών", "Φίλος/Φίλη", "Συγκρούσεις"
    ]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        st.error(f"Λείπουν οι στήλες: {', '.join(missing)}")
    else:
        st.success("✅ Το αρχείο είναι έγκυρο.")
        st.dataframe(df)
