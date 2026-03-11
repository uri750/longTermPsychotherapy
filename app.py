import streamlit as st
import pandas as pd
import re

class MatrixCoder:
    def __init__(self):
        pass

    def is_significant_node(self, text):
        # שלב 2: קביעת משמעות. מחריג שאלות והצהרות קצרות מדי 
        if "?" in text or len(text.strip()) < 2:
            return False
        return True

    def detect_focus(self, text):
        # שלב 3: קביעת המוקד (P/T/D) [cite: 148]
        text_lower = text.lower()
        if any(w in text_lower for w in ["אנחנו", "בינינו", "שנינו", "בחדר"]):
            return "D"
        if any(w in text_lower for w in ["אתה", "את", "שלך"]):
            return "T"
        return "P"

    def detect_dimension(self, text):
        # שלב 4: קביעת המימד לפי סדר עדיפויות: Space -> Content -> Order [cite: 154]
        if any(w in text for w in ["חסום", "ריק", "קפוא", "לא מרגיש", "בור"]):
            return "S"
        if any(w in text for w in ["עצוב", "חושב", "מרגיש", "הלכתי", "הפלה", "הריון"]):
            return "C"
        if any(w in text for w in ["מצד אחד", "אבל", "קונפליקט", "התלבטתי"]):
            return "O"
        return "C"

def process_transcript(text):
    lines = text.split('\n')
    data = []
    coder = MatrixCoder()
    
    for line in lines:
        if not line.strip(): continue
        
        # זיהוי דובר (Speaker) מתוך הטקסט (למשל "אני:" או "הוא:") 
        speaker = "P"
        clean_text = line
        if ":" in line:
            prefix, clean_text = line.split(":", 1)
            if any(w in prefix for w in ["אני", "T", "מטפל"]): speaker = "T"
        
        # שלב 1: פיצול למקטעים (Fragmentation) לפי סימני פיסוק 
        fragments = re.split(r'[.!]', clean_text)
        for frag in fragments:
            frag = frag.strip()
            if not frag: continue
            
            if coder.is_significant_node(frag):
                focus = coder.detect_focus(frag)
                dim = coder.detect_dimension(frag)
                auto_code = f"{speaker}{focus}{dim}"
            else:
                auto_code = "NONE"
            
            data.append({"דובר": speaker, "טקסט": frag, "קידוד MATRIX": auto_code})
    
    return pd.DataFrame(data)

# --- ממשק Streamlit ---
st.set_page_config(layout="wide")
st.title("מערכת קידוד MATRIX - גרסת התמלול המלאה 🧠")

raw_text = st.text_area("הדבק כאן את התמלול (לדוגמה 'אני: שלום. הוא: אני מרגיש חסום'):", height=200)

if st.button("עבד תמלול וקודד"):
    if raw_text:
        df = process_transcript(raw_text)
        st.subheader("תוצאות הקידוד (ניתן לערוך את עמודת הקידוד ישירות בטבלה):")
        
        # שימוש ב-data_editor שמאפשר עריכה ידנית של התוצאות
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        
        st.download_button("הורד תוצאות כ-CSV", edited_df.to_csv(index=False).encode('utf-8-sig'), "matrix_coding.csv")
