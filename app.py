
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

    # Αν υπάρχει στήλη "Παιδί Εκπαιδευτικού", μετονομάζεται αυτόματα σε "Εκπαιδευτ"
    if "Παιδί Εκπαιδευτικού" in df.columns and "Εκπαιδευτ" not in df.columns:
        df.rename(columns={"Παιδί Εκπαιδευτικού": "Εκπαιδευτ"}, inplace=True)

    # Έλεγχος για την ύπαρξη στήλης "Εκπαιδευτ"
    if "Εκπαιδευτ" not in df.columns:
        st.error("❌ Το αρχείο δεν περιέχει τη στήλη 'Εκπαιδευτ'. Παρακαλώ επιβεβαίωσε ότι χρησιμοποιείς το σωστό πρότυπο.")
        st.stop()

    st.success("✅ Το αρχείο ανέβηκε επιτυχώς!")
    st.dataframe(df.head())

    st.subheader("📊 Στατιστικά:")
    st.write("Μαθητές:", len(df))
    st.write("Παιδιά Εκπαιδευτικών:", (df["Εκπαιδευτ"] == "Ναι").sum())
    st.write("Ζωηροί:", (df["Ζωηρός"] == "Ναι").sum())
    st.write("Με Ιδιαιτερότητες:", (df["Ιδιαιτερότητα"] == "Ναι").sum())

except Exception as e:
    st.error(f"⚠️ Παρουσιάστηκε σφάλμα κατά την ανάγνωση του αρχείου:\n{e}")
