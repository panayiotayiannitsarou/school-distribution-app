
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Κατανομή Μαθητών", layout="centered")
st.title("📘 Εφαρμογή Κατανομής Μαθητών")

uploaded_file = st.file_uploader("Ανέβασε αρχείο Excel με μαθητές", type=["xlsx"])
if not uploaded_file:
    st.info("📌 Περιμένω να ανεβάσεις αρχείο Excel...")
    st.stop()

try:
    df = pd.read_excel(uploaded_file)
    # Μετονομασία της στήλης 'Εκπαιδευτ' σε 'Παιδί Εκπαιδευτικού'
    df = df.rename(columns={"Εκπαιδευτ": "Παιδί Εκπαιδευτικού"})

    # Προεπισκόπηση
    st.success("✅ Το αρχείο ανέβηκε επιτυχώς!")
    st.dataframe(df.head())

    # Έλεγχος βασικών στατιστικών
    st.subheader("📊 Στατιστικά:")
    st.write("Μαθητές:", len(df))
    st.write("Παιδιά Εκπαιδευτικών:", (df["Παιδί Εκπαιδευτικού"] == "Ναι").sum())
    st.write("Ζωηροί:", (df["Ζωηρός"] == "Ναι").sum())
    st.write("Με Ιδιαιτερότητες:", (df["Ιδιαιτερότητα"] == "Ναι").sum())

except Exception as e:
    st.error(f"⚠️ Σφάλμα κατά την ανάγνωση του αρχείου: {e}")
