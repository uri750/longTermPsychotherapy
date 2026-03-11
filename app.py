import streamlit as st
import pandas as pd
import re

class MatrixCoder:
    def __init__(self):
        # הגדרת המינוחים בעברית לפי התמונה והמאמר
        self.map = {
            'P': 'מ', 'T': 'ל', 'D': 'ד', # דובר/מוקד: מטופל, מטפל, דיאדה
            'S': 'ר', 'C': 'ת', 'O': 'ס'  # ממד: מרחב, תוכן, סדר
        }

    def is_significant_node(self, text):
        """שלב 2: קביעת משמעות. מחריג שאלות ואירועים מחוץ לחדר [cite: 139, 140]"""
        text_lower = text.lower()
        # החרגת שאלות לפי המדריך [cite: 139]
        if "?" in text or len(text.strip()) < 2:
            return False
        
        # סינון אירועים מחוץ לחדר (רק מה שמתייחס ל-P/T/D בתוך הפגישה) 
        inside_room_keywords = ["אני", "אתה", "את", "אנחנו", "כאן", "עכשיו", "בחדר", "בינינו", "הפגישה", "הקשר", "מרגיש/ה", "חושב/ת"]
        if not any(word in text_lower for word in inside_room_keywords):
            return False
            
        return True

    def detect_focus(self, text):
        """שלב 3: קביעת המוקד (P/T/D) [cite: 147, 148]"""
        text_lower = text.lower()
        if any(w in text_lower for w in ["אנחנו", "בינינו", "שנינו", "בחדר"]):
            return "D"
        if any(w in text_lower for w in ["אתה", "את", "שלך", "אמרת", "שאלת"]):
            return "T"
        return "P"

    def detect_dimension(self, text):
        """שלב 4: קביעת המימד לפי תעדוף: Space -> Content -> Order """
        # 1. מרחב (Space) - יכולת/אי-יכולת לחוות [cite: 54, 59]
        if any(w in text for w in ["חסום", "ריק", "קפוא", "לא מרגיש", "בור", "יכולת", "מסוגל"]):
            return "S"
        # 2. תוכן (Content) - חוויה ספציפית בחדר [cite: 60, 62]
        if any(w in text for w in ["עצוב", "שמח", "כועס", "מרגיש", "חושב", "מסתכל", "מבין"]):
            return "C"
        # 3. סדר (Order) - יחסים בין חוויות או דילמות [cite: 63, 65]
        if any(w in text for w in ["מצד אחד", "אבל", "קונפליקט", "התלבטתי", "דילמה"]):
            return "O"
        return "C"

    def get_explanation(self, focus, dim):
        """מייצר הסבר לקידוד לפי הגדרות המאמר """
        focus_heb = "המטופל" if focus == 'P' else "המטפל" if focus == 'T' else "הדיאדה"
        if dim == 'S':
            return f"התייחסות של {focus_heb} ליכולת או אי-יכולת לחוות (מרחב פוטנציאלי) [cite: 54]"
        elif dim == 'O':
            return f"ניסוח חוקיות, קונפליקט או יחסים בין חוויות של {focus_heb} [cite: 63]"
        else:
            return f"דיווח ישיר על רגש, מחשבה או פעולה קונקרטית בחדר של {focus_heb} [cite: 60]"

def process_transcript(text):
    coder = MatrixCoder()
    lines = text.split('\n')
    data = []
    
    for line in lines:
        if not line.strip(): continue
        speaker = "P" # ברירת מחדל
        clean_text = line
        if ":" in line:
            prefix, clean_text = line.split(":", 1)
            if any(w in prefix for w in ["אני", "T", "מטפל"]): speaker = "T"

        # שלב 1: פרגמנטציה (פיצול לתורי דיבור ומקטעים) [cite: 122, 125]
        fragments = re.split(r'[.!]', clean_text)
        for frag in fragments:
            frag = frag.strip()
            if not frag or not coder.is_significant_node(frag):
                continue
            
            foc = coder.detect_focus(frag)
            dim = coder.detect_dimension(frag)
            
            # בניית הקוד הסופי (דובר-מוקד-ממד)
            final_code = f"{coder.map[speaker]}-{coder.map[foc]}-{coder.map[dim]}"
            
            data.append({
                "מקטע מהתמליל": f'"{frag}"',
                "דובר": "מטפל" if speaker == "T" else "מטופל",
                "מוקד": "מטופל" if foc == 'P' else "מטפל" if foc == 'T' else "דיאדה",
                "ממד": "מרחב" if dim == 'S' else "תוכן" if dim == 'C' else "סדר",
                "קוד סופי": final_code,
                "הסבר הקידוד": coder.get_explanation(foc, dim)
            })
    return pd.DataFrame(data)

# --- Streamlit UI ---
st.set_page_config(layout="wide", page_title="MATRIX Coder")
st.title("מערכת קידוד MATRIX - ניתוח תהליך בתוך החדר 🧠")
st.markdown("מבוסס על *The MATRIX* (Mendlovic et al., 2017) - מסנן אירועים חיצוניים")

input_text = st.text_area("הדבק כאן את התמלול (לדוגמה: 'אני: אני מרגיש חסום כאן בינינו'):", height=200)

if st.button("בצע קידוד MATRIX"):
    if input_text:
        results_df = process_transcript(input_text)
        if not results_df.empty:
            st.subheader("טבלת קידוד מפורטת:")
            # הצגת הטבלה לעריכה
            edited_df = st.data_editor(results_df, use_container_width=True, num_rows="dynamic")
            
            st.divider()
            st.subheader("טבלה סופית להעתקה:")
            st.table(edited_df[["מקטע מהתמליל", "קוד סופי"]])
        else:
            st.warning("לא נמצאו מקטעים משמעותיים המתייחסים להתרחשויות בתוך החדר (בדוק שאין סימני שאלה).")
