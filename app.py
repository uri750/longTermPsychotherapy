import streamlit as st
import pandas as pd
import re

class MatrixCoder:
    def __init__(self):
        self.map = {'P': 'מ', 'T': 'ל', 'D': 'ד', 'S': 'ר', 'C': 'ת', 'O': 'ס'}
        # רשימת "שמות" או ישויות חיצוניות שהמשתמש יכול לעדכן
        self.external_entities = ["נופר", "פריז", "הורים", "בוס", "חברים"]

    def is_significant_node(self, text, history_none_count):
        """
        שלב 2: קביעת משמעות עם חלון הקשר.
        אם המקטעים הקודמים היו חיצוניים, יש סבירות גבוהה שגם הנוכחי הוא NONE.
        """
        text_lower = text.lower()
        
        # 1. החרגת שאלות
        if "?" in text or len(text.strip()) < 2:
            return False, "שאלה או הצהרה קצרה מדי"
            
        # 2. זיהוי סממנים חיצוניים (Ex-room)
        external_markers = ["אתמול", "נפגשתי", "היה", "נסענו", "היינו"] + self.external_entities
        internal_markers = ["בינינו", "בחדר", "הקשר", "עכשיו", "מולי", "איתך"]
        
        has_external = any(word in text_lower for word in external_markers)
        has_internal = any(word in text_lower for word in internal_markers)

        # לוגיקת הקשר: אם אנחנו בתוך "רצף חיצוני" (היסטוריה), נחמיר בסינון
        if has_external or (history_none_count > 0 and not has_internal):
            return False, "אירוע חיצוני (Ex-room) או דמות מחוץ לחדר"
            
        return True, ""

    def detect_focus(self, text):
        """שלב 3: קביעת המוקד (Focus)"""
        text_lower = text.lower()
        if any(w in text_lower for w in ["אנחנו", "בינינו", "שנינו"]): return "D"
        if any(w in text_lower for w in ["אתה", "את", "שלך"]): return "T"
        return "P"

    def detect_dimension(self, text):
        """שלב 4: קביעת המימד לפי תעדוף: Space -> Content -> Order"""
        if any(w in text for w in ["חסום", "ריק", "קפוא", "לא מרגיש", "יכולת"]): return "S"
        if any(w in text for w in ["מצד אחד", "אבל", "קונפליקט", "דילמה"]): return "O"
        return "C"

def process_transcript(text):
    coder = MatrixCoder()
    lines = text.split('\n')
    results = []
    history_none_count = 0 # מונה כמה מקטעים אחרונים היו NONE
    
    for line in lines:
        if not line.strip(): continue
        speaker = "P"
        if ":" in line:
            prefix, line = line.split(":", 1)
            if any(w in prefix for w in ["אני", "T", "מטפל"]): speaker = "T"

        fragments = re.split(r'[.!]', line)
        for frag in fragments:
            frag = frag.strip()
            if not frag: continue
            
            is_node, reason = coder.is_significant_node(frag, history_none_count)
            
            if is_node:
                foc = coder.detect_focus(frag)
                dim = coder.detect_dimension(frag)
                code = f"{coder.map[speaker]}-{coder.map[foc]}-{coder.map[dim]}"
                explanation = f"דיווח בחדר של {coder.map[foc]} במימד ה{dim}" # מפשט להסבר קצר
                history_none_count = 0 # איפסנו את הרצף החיצוני
            else:
                code = "NONE"
                explanation = reason
                history_none_count += 1 # אנחנו ברצף חיצוני
            
            results.append({
                "מקטע מהתמליל": f'"{frag}"',
                "קוד MATRIX": code,
                "הסבר הקידוד": explanation
            })
    return pd.DataFrame(results)

# --- ממשק Streamlit עם תיקון RTL ---
st.set_page_config(layout="wide")
# הזרקת CSS לתיקון כיוון הטבלה והטקסט לימין
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    table { direction: rtl; margin-left: auto; margin-right: 0; }
    th, td { text-align: right !important; }
    div[data-testid="stTable"] { direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

st.title("מערכת קידוד MATRIX - ניתוח הקשרי 🧠")

input_text = st.text_area("הדבק את התמלול כאן:", height=200)

if st.button("בצע קידוד"):
    if input_text:
        df = process_transcript(input_text)
        st.subheader("תוצאות הקידוד (מימין לשמאל):")
        # הטבלה עכשיו תוצג עם המקטע מימין, הקוד באמצע וההסבר משמאל
        st.table(df[["מקטע מהתמליל", "קוד MATRIX", "הסבר הקידוד"]])
