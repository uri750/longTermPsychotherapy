import streamlit as st
import pandas as pd

class MatrixCoder:
    def __init__(self):
        self.focus_options = ['P', 'T', 'D']
        self.dimension_options = ['S', 'C', 'O']

    def is_significant_node(self, text):
        # שלב 2: קביעת משמעות. מחריג שאלות והצהרות לא מובנות
        if "?" in text or "מממ" in text or len(text.strip()) < 2:
            return False
        return True

    def detect_focus(self, text):
        # שלב 3: קביעת המוקד (מי נושא ההצהרה)
        text = text.lower()
        if any(word in text for word in ["אנחנו", "בינינו", "שנינו", "בחדר"]):
            return "D"
        if any(word in text for word in ["אתה", "את", "שלך"]):
            return "T"
        return "P"

    def detect_dimension(self, text):
        # שלב 4: קביעת המימד לפי האלגוריתם הקבוע: Space -> Content -> Order
        
        # 1. בדיקת Space (פוטנציאל לחוויה)
        if any(word in text for word in ["חסום", "ריק", "קפוא", "לא מרגיש", "בור"]):
            return "S"
            
        # 2. בדיקת Content (חוויה ספציפית)
        if any(word in text for word in ["עצוב", "חושב", "מרגיש", "הלכתי", "הפלה", "הריון"]):
            return "C"
            
        # 3. בדיקת Order (יחסים בין חוויות/קונפליקטים)
        if any(word in text for word in ["מצד אחד", "אבל", "קונפליקט", "התלבטתי"]):
            return "O"
            
        return "C"

    def code_fragment(self, speaker, text):
        if not self.is_significant_node(text):
            return "NONE"
        
        focus = self.detect_focus(text)
        dimension = self.detect_dimension(text)
        return f"{speaker}{focus}{dimension}"

# --- ממשק Streamlit ---
st.title("מערכת קידוד MATRIX 🧠")
coder = MatrixCoder()

speaker = st.selectbox("מי הדובר?", ["T", "P"])
text_input = st.text_area("הכנס פרגמנט לקידוד:")

if st.button("בצע קידוד"):
    if text_input:
        res = coder.code_fragment(speaker, text_input)
        st.info(f"התוצאה: **{res}**")
