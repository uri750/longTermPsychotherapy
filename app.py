import streamlit as st
import pandas as pd

# הגדרות המערכת והמילון בעברית
DIMENSIONS = {"ר": "מרחב (Space)", "ת": "תוכן (Content)", "ס": "סדר (Order)"}
FOCUS = {"מ": "מטופל (Patient)", "פל": "מטפל (Therapist)", "צ": "צמד (Dyad)"}

st.set_page_config(page_title="מקודד המטריקס", layout="wide")

st.title("מערכת קידוד פגישות - לפי מודל המטריצה")
st.write("הדבק תמליל וקבל קידוד אוטומטי עם אפשרות לעריכה ידנית.")

# 1. ממשק קלט
text_input = st.text_area("הדבק את הטקסט כאן:", height=300)

if text_input:
    # 2. לוגיקת עיבוד ראשונית (סימולציה של חלוקה למקטעים)
    # כאן בעתיד יתחבר ה-API של המודל לקידוד אוטומטי
    lines = [line.strip() for line in text_input.split('\n') if line.strip()]
    
    data = []
    for line in lines:
        # ברירת מחדל לקידוד (ניתן לעריכה ידנית)
        data.append({
            "טקסט מקורי": line,
            "דובר": "מטופל" if "הוא:" in line else "מטפל",
            "מוקד": "מטופל",
            "ממד": "תוכן",
            "קוד סופי": "מ-מ-ת"
        })
    
    df = pd.DataFrame(data)

    # 3. ממשק עריכה ידנית (Data Editor)
    st.subheader("עריכת קידוד (לחץ על תא כדי לשנות)")
    edited_df = st.data_editor(
        df,
        column_config={
            "מוקד": st.column_config.SelectboxColumn(options=["מטופל", "מטפל", "צמד"]),
            "ממד": st.column_config.SelectboxColumn(options=["מרחב", "תוכן", "סדר"]),
        },
        num_rows="dynamic",
        use_container_width=True
    )

    # 4. ייצוא נתונים
    st.divider()
    csv = edited_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("הורד קובץ אקסל (CSV)", csv, "coding_results.csv", "text/csv")