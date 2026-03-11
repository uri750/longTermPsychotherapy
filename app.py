import streamlit as st
import pandas as pd
import re

class MatrixCoder:
    def is_significant_node(self, text):
        # שלב 2: סינון שאלות והצהרות לא מובנות [cite: 139]
        if "?" in text or len(text.strip()) < 2:
            return False
        return True

    def detect_focus(self, text):
        # שלב 3: זיהוי מוקד (Focus) [cite: 147, 148]
        text_lower = text.lower()
        if any(w in text_lower for w in ["אנחנו", "בינינו", "שנינו", "בחדר"]):
            return "D" # Dyad [cite: 50, 51]
        if any(w in text_lower for w in ["אתה", "את", "שלך"]):
            return "T" # Therapist [cite: 149]
        return "P" # Patient [cite: 149]

    def detect_dimension(self, text):
        # שלב 4: זיהוי מימד (Dimension) לפי סדר עדיפויות [cite: 154]
        if any(w in text for w in ["חסום", "ריק", "קפוא", "לא מרגיש", "בור"]):
            return "S" # Space [cite: 59]
        if any(w in text for w in ["מצד אחד", "אבל", "קונפליקט", "התלבטתי"]):
            return "O" # Order [cite: 64]
        return "C" # Content [cite: 60]

def process_transcript(text):
    lines = text.split('\n')
    data = []
    coder = MatrixCoder()
    
    for line in lines:
        if not line.strip(): continue
        
        # זיהוי דובר ראשוני
        speaker = "P"
        clean_text = line
        if ":" in line:
            prefix, clean_text = line.split(":", 1)
            if any(w in prefix for w in ["אני", "T", "מטפל", "מטפלת"]): speaker = "T"
        
        # שלב 1: פרגמנטציה (פיצול לפי נקודות/סימני קריאה) 
        fragments = re.split(r'[.!]', clean_text)
        for frag in fragments:
            frag = frag.strip()
            if not frag: continue
            
            if coder.is_significant_node(frag):
                focus = coder.detect_focus(frag)
                dim = coder.detect_dimension(frag)
                # יצירת קוד 3 האותיות המדויק [cite: 159, 160]
                auto_code = f"{speaker}{focus}{dim}"
            else:
                auto_code = "NONE" [cite: 146]
            
            data.append({"טקסט": frag, "קידוד MATRIX": auto_code})
    
    return pd.DataFrame(data)

# --- ממשק Streamlit ---
st.set_page_config(layout="wide", page_title="MATRIX Output Tool")
st.title("מערכת קידוד MATRIX - פלט נקי 🧠")

raw_text = st.text_area("הדבק כאן את התמלול:", height=150)

if raw_text:
    if st.button("עבד וקודד"):
        df = process_transcript(raw_text)
        st.session_state['matrix_df'] = df

if 'matrix_df' in st.session_state:
    st.subheader("ערוך את הקידוד במידת הצורך:")
    # טבלה לעריכה
    edited_df = st.data_editor(st.session_state['matrix_df'], use_container_width=True)
    
    st.divider()
    
    # הצגת טבלה נקייה להעתקה
    st.subheader("טבלה סופית להעתקה (טקסט + קוד):")
    clean_df = edited_df[["טקסט", "קידוד MATRIX"]]
    
    # הצגה כטבלה סטטית שנוח לסמן עם העכבר ולהעתיק
    st.table(clean_df)
    
    # אפשרות להצגת קוד Markdown להעתקה מהירה לאפליקציות אחרות
    if st.checkbox("הצג כטקסט להעתקה (Markdown)"):
        st.code(clean_df.to_markdown(index=False))
