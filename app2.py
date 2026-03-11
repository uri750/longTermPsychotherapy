import streamlit as st
import pandas as pd
import google.generativeai as genai
import json

# 1. הכנס את מפתח ה-API שלך כאן
API_KEY = "AIzaSyANFUVovsAnswVOtQsd1YybDdYGhyjoI-E" 

def analyze_transcript(transcript):
    genai.configure(api_key=API_KEY)
    
    # שימוש במודל המהיר והמעודכן ביותר
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    אתה מומחה קליני בקידוד תמלילי פסיכותרפיה לפי מודל MATRIX (Mendlovic et al., 2017).
    
    חוקי הקידוד:
    1. פצל את התמליל למקטעים קצרים (משפטים/תורי דיבור).
    2. חוק ה-Ex-room: כל מקטע שמתאר אירוע חיצוני, דיווח על העבר, או מתייחס לצד ג' (כמו "נופר" או "נסיעה לפריז") - יקבל את הקוד NONE.
    3. שאלות יקבלו את הקוד NONE.
    4. התייחסות ל"כאן ועכשיו" בחדר הטיפולים תקבל קוד בן 3 אותיות (למשל מ-מ-ת, ל-ד-ר).
    
    התמליל לניתוח:
    {transcript}
    
    עליך להחזיר מערך JSON של אובייקטים. לכל אובייקט יהיו בדיוק 3 המפתחות הבאים באנגלית:
    "text" (המקטע מתוך התמליל), "code" (הקוד או NONE), "explanation" (הסבר קצר בעברית).
    """

    try:
        # 2. כפיית פלט JSON ברמת ה-API - פותר את כל שגיאות הפענוח!
        result = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        
        # 3. טעינת הנתונים והמרתם לטבלה
        data = json.loads(result.text)
        df = pd.DataFrame(data)
        
        # 4. שינוי שמות העמודות לעברית להצגה
        df.columns = ["מקטע מהתמליל", "קוד MATRIX", "הסבר הקידוד"]
        return df

    except Exception as e:
        st.error(f"התרחשה שגיאה בתקשורת מול ה-API: {e}")
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
    if API_KEY == "YOUR_API_KEY_HERE":
        st.warning("נא לעדכן מפתח API חוקי בקוד.")
    elif user_text.strip() == "":
        st.warning("נא להזין טקסט לניתוח.")
    else:
        with st.spinner("מנתח את התמליל..."):
            results_df = analyze_transcript(user_text)
            if not results_df.empty:
                st.success("הניתוח הושלם בהצלחה!")
                st.table(results_df)
