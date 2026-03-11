import streamlit as st
import pandas as pd
import re

class MatrixCoder:
    def __init__(self):
        # מילות מפתח לזיהוי ראשוני
        self.space_keywords = ["חסום", "ריק", "קפוא", "לא מרגיש", "בור", "לא מסוגל"]
        self.order_keywords = ["מצד אחד", "אבל", "קונפליקט", "התלבטתי", "דילמה"]
        self.content_keywords = ["עצוב", "חושב", "מרגיש", "הלכתי", "הפלה", "הריון"]

    def is_significant_node(self, text):
        # שלב 2: קביעת משמעות. מחריג שאלות והצהרות קצרות מדי
        if "?" in text or len(text.strip()) < 2:
            return False
        return True

    def detect_focus(self, text):
        # שלב 3: קביעת המוקד (P/T/D)
        text_lower = text.lower()
        if any(w in text_lower for w in ["אנחנו", "בינינו", "שנינו", "בחדר"]):
            return "D"
        if any(w in text_lower for w in ["אתה", "את", "שלך"]):
            return "T"
        return "P"

    def detect_dimension(self, text):
        # שלב 4: קביעת המימד לפי האלגוריתם הקבוע: Space -> Content -> Order
        
        # 1. בדיקת Space (פוטנציאל לחוויה)
        if any(word in text for word in self.space_keywords):
            return "S"
            
        # 2. בדיקת Content (חוויה ספציפית)
        if any(word in text for word in self.content_keywords):
            return "C"
            
        # 3. בדיקת Order (יחסים בין חוויות/קונפליקטים)
        if any(word in text for word in self.order_keywords):
            return "O"
            
        return "C"

    def code_fragment(self, speaker, text):
        if not self.is_significant_node(text):
            return "NONE"
        
        focus = self.detect_focus(text)
        dimension = self.detect_dimension(text)
        # הרכבת קוד שלוש האותיות
        return f"{speaker}{focus}{dimension}"

def process_transcript(text):
    lines = text.split('\n')
    data = []
    coder = MatrixCoder()
    
    for line in lines:
        if not line.strip(): continue
        
        # זיהוי הדובר בתחילת השורה
        speaker = "P"
        clean_text = line
        if ":" in line:
            prefix, clean_text = line.split(":", 1)
            if any(w in prefix for w in ["אני", "T", "מטפל"]): 
                speaker = "T"
        
        # שלב 1: פרגמנטציה (פיצול לפי נקודות/סימני קריאה)
        fragments = re.split(r'[.!]', clean_text)
        for frag in fragments:
            frag = frag.strip()
            if not frag: continue
            
            auto_code = coder.code_fragment(speaker, frag)
            data.append({"טקסט": frag, "קידוד MATRIX": auto_code})
    
    return pd.DataFrame(data)

# --- ממשק Streamlit ---
st.set_page_config(layout="wide")
st.title("מערכת קידוד MATRIX - פלט נקי 🧠")

raw_text = st.text_area("הדבק כאן את התמלול:", height=200)

if st.button("עבד וקודד"):
    if raw_text:
        df = process_transcript(raw_text)
        st.session_state['matrix_df'] = df

if 'matrix_df' in st.session_state:
    st.subheader("ערוך את הקידוד במידת הצורך:")
    edited_df = st.data_editor(st.session_state['matrix_df'], use_container_width=True)
    
    st.divider()
    st.subheader("טבלה סופית להעתקה:")
    st.table(edited_df[["טקסט", "קידוד MATRIX"]])
