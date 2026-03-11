import streamlit as st
import pandas as pd
import re

class MatrixCoder:
    def __init__(self):
        # מיפוי אותיות לעברית (דובר/מוקד/ממד)
        self.map = {
            'P': 'מ', 'T': 'ל', 'D': 'ד', # מטופל, מטפל, דיאדה
            'S': 'ר', 'C': 'ת', 'O': 'ס'  # מרחב, תוכן, סדר
        }

    def is_significant_node(self, text):
        """שלב 2: סינון קפדני של אירועים מחוץ לחדר ושאלות"""
        text_lower = text.lower()
        
        # 1. החרגת שאלות (סימן שאלה)
        if "?" in text or len(text.strip()) < 2:
            return False
            
        # 2. סינון אירועים חיצוניים (דיווחים על העבר/צד ג' מחוץ לפגישה)
        # אם המשפט מכיל מילות עבר חיצוניות ללא קישור ל"כאן ועכשיו", הוא נפסל
        external_markers = ["אתמול", "נפגשתי", "היתה", "היה שם", "הם", "מחוץ"]
        internal_markers = ["אני", "אתה", "את", "אנחנו", "עכשיו", "בחדר", "בינינו", "הפגישה", "מרגיש/ה", "חושב/ת"]
        
        # אם יש סממנים חיצוניים ואין סממנים חזקים של ה"כאן ועכשיו" - זה NONE
        if any(word in text_lower for word in external_markers) and not any(word in text_lower for word in ["בינינו", "בחדר", "הקשר שלנו"]):
            return False
            
        return True

    def detect_focus(self, text):
        """שלב 3: קביעת המוקד (P/T/D) בתוך החדר"""
        text_lower = text.lower()
        if any(w in text_lower for w in ["אנחנו", "בינינו", "שנינו", "בחדר"]):
            return "D"
        if any(w in text_lower for w in ["אתה", "את", "שלך", "אמרת", "שאלת"]):
            return "T"
        return "P"

    def detect_dimension(self, text):
        """שלב 4: קביעת המימד: מרחב -> תוכן -> סדר"""
        # מרחב (Space) - יכולת לחוות
        if any(w in text for w in ["חסום", "ריק", "קפוא", "לא מרגיש", "בור", "יכולת"]):
            return "S"
        # סדר (Order) - יחסים וקונפליקטים
        if any(w in text for w in ["מצד אחד", "אבל", "קונפליקט", "דילמה"]):
            return "O"
        return "C"

    def get_explanation(self, focus, dim):
        """הסבר הקידוד לפי המאמר"""
        focus_name = "המטופל" if focus == 'P' else "המטפל" if focus == 'T' else "הדיאדה"
        if dim == 'S':
            return f"התייחסות של {focus_name} ליכולת או אי-יכולת לחוות (מרחב פוטנציאלי) "
        elif dim == 'O':
            return f"ניסוח קונפליקט או יחסים בין חוויות של {focus_name} (סדר) [cite: 63]"
        else:
            return f"דיווח ישיר על רגש, מחשבה או פעולה בחדר של {focus_name} (תוכן) "

def process_transcript(text):
    coder = MatrixCoder()
    lines = text.split('\n')
    results = []
    
    for line in lines:
        if not line.strip(): continue
        speaker = "P"
        clean_text = line
        if ":" in line:
            prefix, clean_text = line.split(":", 1)
            if any(w in prefix for w in ["אני", "T", "מטפל"]): speaker = "T"

        # פרגמנטציה (פיצול לפי נקודות)
        fragments = re.split(r'[.!]', clean_text)
        for frag in fragments:
            frag = frag.strip()
            if not frag: continue
            
            if coder.is_significant_node(frag):
                foc = coder.detect_focus(frag)
                dim = coder.detect_dimension(frag)
                code = f"{coder.map[speaker]}-{coder.map[foc]}-{coder.map[dim]}"
                explanation = coder.get_explanation(foc, dim)
            else:
                code = "NONE"
                explanation = "אירוע חיצוני או שאלה - לא מקודד לפי המודל [cite: 139, 140]"
            
            results.append({
                "מקטע מהתמליל": f'"{frag}"',
                "קוד MATRIX": code,
                "הסבר הקידוד": explanation
            })
    return pd.DataFrame(results)

# --- Streamlit UI ---
st.set_page_config(layout="wide")
st.markdown("""<style> .main {direction: rtl;} div.stButton > button {width: 100%;} </style>""", unsafe_allow_html=True)

st.title("מערכת קידוד MATRIX - ניתוח פנים-טיפולי 🧠")

input_text = st.text_area("הדבק את התמלול כאן:", height=200)

if st.button("בצע קידוד"):
    if input_text:
        df = process_transcript(input_text)
        st.subheader("תוצאות הקידוד (מימין לשמאל):")
        # הצגת הטבלה לפי הסדר המבוקש
        st.table(df[["מקטע מהתמליל", "קוד MATRIX", "הסבר הקידוד"]])
