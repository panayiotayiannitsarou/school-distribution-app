
import streamlit as st
import pandas as pd

st.title("📘 Εφαρμογή Κατανομής Μαθητών")

uploaded_file = st.file_uploader("Ανέβασε αρχείο Excel με μαθητές", type=["xlsx"])
if not uploaded_file:
    st.info("📌 Περιμένω να ανεβάσεις αρχείο Excel...")
    st.stop()

try:
    students_df = pd.read_excel(uploaded_file)
    st.success("✅ Το αρχείο ανέβηκε επιτυχώς!")
    st.dataframe(students_df.head())
except Exception as e:
    st.error(f"⚠️ Σφάλμα κατά την ανάγνωση του αρχείου: {e}")
