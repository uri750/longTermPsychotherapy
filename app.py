import streamlit as st
import pandas as pd

class MatrixCoder:
    def __init__(self):
        self.focus_options = ['P', 'T', 'D']  # Patient, Therapist, Dyad [cite: 48]
        self.dimension_options = ['S', 'C', 'O']  # Space, Content, Order [cite: 53]

    def is_significant_node(self, text):
        """
        שלב 2: קביעת משמעות (Significance) [cite: 137]
        מחריג שאלות, הצעות, הצהרות לא מובנות או נושאים שאינם P/T/D[cite: 138, 139, 140].
        """
        if "?" in text or "מממ" in text or len(text.strip()) < 2:
            return False [cite: 139]
        return True

    def detect_focus(self, text):
        """
        שלב 3: קביעת המוקד (Focus) [cite: 147, 148]
        מי נושא ההצהרה? (לא בהכרח הדובר) [cite: 150].
        """
        text = text.lower()
        if any(word in text for word in ["אנחנו", "בינינו", "שנינו", "בחדר"]):
            return "D"  # Dyad [cite: 50, 51]
        if any(word in text for word in ["אתה", "את", "שלך"]):
            return "T"  # Therapist (כשמטופל מדבר על המטפל) [cite: 149]
        return "P"  # ברירת מחדל: Patient [cite: 149]

    def detect_dimension(self, text):
        """
        שלב 4: קביעת המימד (Dimension) לפי אלגוריתם קבוע[cite: 152, 154].
        תעדוף: Space -> Content -> Order.
        """
        # 1. בדיקת Space: פוטנציאל לחוויה / יכולת לחוות [cite: 54, 55]
        if any(word in text for word in ["חסום", "ריק", "קפוא", "לא מרגיש", "בור"]):
            return "S" [cite: 59]
            
        # 2. בדיקת Content: חוויה ספציפית (רגש, מחשבה, פעולה) [cite: 60]
        if any(word in text for word in ["עצוב", "חושב", "מרגיש", "הלכתי"]):
            return "C" [cite: 60, 61]
            
        # 3. בדיקת Order: יחסים בין חוויות, דילמות, קונפליקטים [cite: 63]
        if any(word in text for word in ["מצד אחד", "אבל", "קונפליקט", "התלבטתי"]):
            return "O" [cite: 64]
            
        return "C"  # ברירת מחדל כפי שמופיע בדוגמאות [cite: 68, 92]

    def code_fragment(self, speaker, text):
        """האלגוריתם המלא לקידוד פרגמנט[cite: 158, 159]."""
        if not self.is_significant_node(text):
            return "NONE" [cite: 146, 157]
        
        focus = self.detect_focus(text)
        dimension = self.detect_dimension(text)
        
        # החזרת קוד בן 3 אותיות: דובר, מוקד, מימד [cite: 159]
        return f"{speaker}{focus}{dimension}"

# --- ממשק Streamlit ---
st.set_page_config(page_title="The MATRIX Coder", layout="centered")
st.title("מערכת קידוד MATRIX 🧠")
st.write("מבוסס על המודל של מנדלוביץ' ושות' (2017)")

coder = MatrixCoder()

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        speaker = st.selectbox("מי הדובר?", ["T", "P"], help="T = Therapist, P = Patient")
    with col2:
        text_input = st.text_area("הכנס פרגמנט לקידוד:", placeholder="למשל: אני מרגיש חסום...")

if st.button("בצע קידוד"):
    if text_input:
        res = coder.code_fragment(speaker, text_input)
        st.info(f"התוצאה: **{res}**")
        
        if res == "NONE":
            st.warning("הפרגמנט סומן כלא משמעותי (למשל: שאלה או קצר מדי) ")
        else:
            st.success(f"דובר: {res[0]} | מוקד: {res[1]} | מימד: {res[2]}")
