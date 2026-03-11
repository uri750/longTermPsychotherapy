import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import re

# 1. הכנס את המפתח שלך בין המרכאות:
API_KEY = "AIzaSyAFucDqwsxfg2WGLhV3OKnMroBH_pQ2U08" 

def analyze_transcript(transcript):
    clean_key = API_KEY.strip()
    genai.configure(api_key=clean_key)
    
    # --- מנגנון אוטומטי למציאת מודל תקין (מונע שגיאות 404) ---
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if not available_models:
            st.error("לא נמצאו מודלים מאושרים למפתח שלך בשרתי גוגל.")
            return pd.DataFrame()
            
        # בחירה אוטומטית במודל הראשון שהשרת מדווח כפעיל
        chosen_model_name = available_models[0]
        
        # אם יש מודל מתקדם מסדרת 1.5 או Pro, נעדיף אותו
        for name in available_models:
            if 'flash' in name:
                chosen_model_name = name
                break
                
        model = genai.GenerativeModel(chosen_model_name)
    except Exception as setup_error:
        st.error(f"שגיאה בהתחברות לשרתי גוגל: {setup_error}")
        return pd.DataFrame()
    # ---------------------------------------------------------
    
    prompt = f"""
    אתה מומחה קליני בקידוד תמלילי פסיכותרפיה לפי מודל MATRIX (Mendlovic et al., 2017).
    
    חוקי הקידוד:
    1. פצל את התמליל למקטעים קצרים (משפטים/תורי דיבור).
    2. חוק ה-Ex-room: כל מקטע שמתאר אירוע חיצוני, דיווח על העבר, או מתייחס לצד ג' (כמו שמות של אנשים אחרים) - יקבל את הקוד NONE.
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
        if len(df.columns) >= 3:
            df = df.iloc[:, :3] # לוקח רק את 3 העמודות הראשונות
            df.columns = ["מקטע מהתמליל", "קוד MATRIX", "הסבר הקידוד"]
        return df

    except Exception as e:
        st.error("התרחשה שגיאה במהלך ניתוח התמלול:")
        st.error(str(e))
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
        with st.spinner("מוצא מודל זמין ומנתח את התמליל..."):
            results_df = analyze_transcript(user_text)
            if not results_df.empty:
                st.success("הניתוח הושלם בהצלחה!")
                st.table(results_df)
