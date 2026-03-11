import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import re

# הדבק כאן את מפתח ה-API שלך:
API_KEY = "YOUR_API_KEY_HERE" 
genai.configure(api_key=API_KEY)

def analyze_transcript_with_ai(transcript):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    system_prompt = """
    אתה מומחה קליני בקידוד תמלילי פסיכותרפיה לפי מודל MATRIX (Mendlovic et al., 2017).
    1. קבל תמליל ופצל למקטעים קצרים.
    2. קודד כל מקטע תוך הבנת ההקשר הנרטיבי המלא.
    3. חוק ה-Ex-room: אירוע חיצוני, דיווח על העבר, או צד ג' - החזר NONE.
    4. חוק השאלות: שאלות - החזר NONE.
    5. "כאן ועכשיו" בחדר - החזר קוד (מ/ל-מ/ל/ד-ר/ת/ס).
    
    החזר אך ורק רשימת JSON חוקית. הנה המבנה הנדרש:
    [
      {"text": "המקטע", "code": "הקוד", "exp": "הסבר"}
    ]
    """
    
    try:
        response = model.generate_content(system_prompt + "\n\nהתמליל:\n" + transcript)
        raw_text = response.text
        
        # חילוץ ה-JSON נטו
        match = re.search(r'\[.*\]', raw_text, re.DOTALL)
        if match:
            json_str = match.group(0)
        else:
            json_str = raw_text
            
        data = json.loads(json_str.strip())
        
        # "חסין כדורים": מתעלם מהשמות שה-AI נתן ולוקח רק את הערכים עצמם
        clean_rows = []
        for item in data:
            if isinstance(item, dict):
                vals = list(item.values())
            elif isinstance(item, list):
                vals = item
            else:
                continue
                
            # מבטיח שתמיד יהיו בדיוק 3 עמודות (משלים בריק אם חסר, חותך אם יש עודף)
            vals = vals + [""] * (3 - len(vals))
            clean_rows.append(vals[:3])
            
        # בניית טבלה חדשה ונקייה
        df = pd.DataFrame(clean_rows, columns=["מקטע מהתמליל", "קוד MATRIX", "הסבר הקידוד"])
        return df
        
    except Exception as e:
        st.error(f"שגיאה בפענוח הנתונים מהמודל. הנה מה שהמודל החזיר:")
        try:
            st.code(raw_text)
        except:
            st.write(e)
        return pd.DataFrame()

# --- עיצוב הממשק (RTL) ---
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    table { direction: rtl; margin-left: auto; margin-right: 0; }
    th, td { text-align: right !important; }
    div[data-testid="stTable"] { direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

st.title("מערכת קידוד MATRIX - מבוססת AI 🧠")
st.write("מנתח את ההקשר הנרטיבי כדי לסנן אירועי Ex-room ולזהות את הכאן-ועכשיו.")

transcript_input = st.text_area("הדבק את התמלול כאן:", height=200)

if st.button("נתח באמצעות בינה מלאכותית"):
    if API_KEY == "YOUR_API_KEY_HERE":
        st.warning("שים לב: עליך להכניס מפתח API פעיל בקוד כדי שהניתוח יעבוד.")
    elif transcript_input:
        with st.spinner("ה-AI קורא את התמליל ומנתח הקשרים..."):
            df = analyze_transcript_with_ai(transcript_input)
            
            if not df.empty:
                st.success("הניתוח הושלם!")
                st.table(df)
