import streamlit as st
import pandas as pd
import google.generativeai as genai
import json

# כאן תצטרך להכניס את מפתח ה-API שלך
# אפשר גם להגדיר את זה בצורה מאובטחת דרך st.secrets
API_KEY = "YOUR_API_KEY_HERE" 
genai.configure(api_key=API_KEY)

def analyze_transcript_with_ai(transcript):
    model = genai.GenerativeModel('gemini-1.5-flash') # או מודל מתקדם יותר
    
    system_prompt = """
    אתה מומחה קליני בקידוד תמלילי פסיכותרפיה לפי מודל MATRIX (Mendlovic et al., 2017).
    משימתך:
    1. קבל את התמליל ופצל אותו למקטעים קצרים (תורי דיבור ומשפטים).
    2. קודד כל מקטע תוך הבנת ההקשר המלא של הפגישה (חלון הקשר נרטיבי).
    3. חוק ה-Ex-room: אם המקטע הוא חלק מסיפור על אירוע מחוץ לחדר, דיווח על העבר, או מתייחס לדמויות חיצוניות שאינן בדיאדה - עליך להחזיר תמיד NONE.
    4. חוק השאלות: שאלות אינן מקודדות (החזר NONE).
    5. אם המקטע מתייחס ל"כאן ועכשיו" בחדר הטיפולים, החזר קוד בן 3 אותיות לפי המפתח הבא:
       - דובר: מ (מטופל), ל (מטפל).
       - מוקד: מ (מטופל), ל (מטפל), ד (דיאדה).
       - ממד (לפי סדר עדיפויות): ר (מרחב - פוטנציאל לחוות), ת (תוכן - חוויה קונקרטית/רגש), ס (סדר - קונפליקט/התלבטות).
       
    החזר את התשובה *אך ורק* כרשימת JSON חוקית במבנה הבא (ללא טקסט נוסף):
    [
      {"fragment": "מקטע מהתמליל", "code": "מ-מ-ת", "explanation": "הסבר קצר על הקידוד או מדוע זה NONE"},
      ...
    ]
    """
    
    try:
        response = model.generate_content(system_prompt + "\n\nהתמליל:\n" + transcript)
        
        # ניקוי הפלט כדי לוודא שזה JSON נקי
        raw_text = response.text
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[1].split("```")[0]
        elif "```" in raw_text:
            raw_text = raw_text.split("```")[1].split("```")[0]
            
        data = json.loads(raw_text.strip())
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"שגיאה בניתוח: {e}")
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
                # שינוי שמות העמודות לעברית והצגה מימין לשמאל
                df = df.rename(columns={
                    "fragment": "מקטע מהתמליל", 
                    "code": "קוד MATRIX", 
                    "explanation": "הסבר הקידוד"
                })
                
                st.success("הניתוח הושלם!")
                st.table(df[["מקטע מהתמליל", "קוד MATRIX", "הסבר הקידוד"]])
