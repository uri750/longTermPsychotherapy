import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import re

# 1. הכנס את המפתח שלך בין המרכאות:
API_KEY = "AIzaSyDNzs0LRyc-TsYUH_WUgwK5o-ZN4A6VAsM" 

def analyze_transcript(transcript):
    # ניקוי אוטומטי של רווחים נסתרים מהמפתח למניעת שגיאת 400
    clean_key = API_KEY.strip()
    genai.configure(api_key=clean_key)
    
    # שימוש במודל הקלאסי שנתמך בכל גרסאות הספריה ללא בעיות תאימות
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""
    אתה מומחה קליני בקידוד תמלילי פסיכותרפיה לפי מודל MATRIX (Mendlovic et al., 2017).
    
    חוקי הקידוד:
    1. פצל את התמליל למקטעים קצרים (משפטים/תורי דיבור).
    2. חוק ה-Ex-room: כל מקטע שמתאר אירוע חיצוני, דיווח על העבר, או מתייחס לצד ג' (כמו "נופר" או "פריז") - יקבל את הקוד NONE.
    3. שאלות יקבלו את הקוד NONE.
    4. התייחסות ל"כאן ועכשיו" בחדר הטיפולים תקבל קוד בן 3 אותיות (למשל מ-מ-ת, ל-ד-ר).
    
    התמליל לניתוח:
    {transcript}
    
    עליך להחזיר אך ורק מערך JSON נקי, ללא שום טקסט מקדים. 
    לכל אובייקט יהיו בדיוק 3 המפתחות הבאים באנגלית:
    "text", "code", "explanation".
    """

    try:
        result = model.generate_content(prompt)
        raw_text = result.text
        
        # חילוץ ה-JSON בבטחה
        match = re.search(r'\[.*\]', raw_text, re.DOTALL)
        if match:
            clean_json = match.group(0)
        else:
            clean_json = raw_text
            
        data = json.loads(clean_json)
        df = pd.DataFrame(data)
        
        # התאמת שמות העמודות
        if len(df.columns) == 3:
            df.columns = ["מקטע מהתמליל", "קוד MATRIX", "הסבר הקידוד"]
        return df

    except Exception as e:
        st.error("התרחשה שגיאה מול השרת של גוגל:")
        st.error(str(e))
        if hasattr(e, 'message'):
            st.write("פרטי שגיאה מדויקים:", e.message)
        return pd.DataFrame()

# --- ממשק המשתמש ---
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    table { direction: rtl; margin-left: auto; margin-right: 0; }
    th, td { text-align: right !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("מערכת קידוד MATRIX 🧠")
st.write("מנתח הקשר נרטיבי ומזהה אירועי Ex-room באמצעות בינה מלאכותית.")

user_text = st.text_area("הדבק את התמלול כאן:", height=200)

if st.button("בצע קידוד"):
    if "YOUR_API_KEY_HERE" in API_KEY or API_KEY.strip() == "":
        st.warning("נא לעדכן מפתח API חוקי בקוד (שורה 8).")
    elif user_text.strip() == "":
        st.warning("נא להזין טקסט לניתוח.")
    else:
        with st.spinner("מנתח את התמליל (זה עשוי לקחת מספר שניות)..."):
            results_df = analyze_transcript(user_text)
            if not results_df.empty:
                st.success("הניתוח הושלם בהצלחה!")
                st.table(results_df)
