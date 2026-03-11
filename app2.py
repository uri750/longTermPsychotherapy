import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import re

# הדבק כאן את מפתח ה-API שלך במקום הטקסט בפנים:
API_KEY = "YOUR_API_KEY_HERE" 
genai.configure(api_key=API_KEY)

def analyze_transcript_with_ai(transcript):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    system_prompt = """
    אתה מומחה קליני בקידוד תמלילי פסיכותרפיה לפי מודל MATRIX (Mendlovic et al., 2017).
    משימתך:
    1. קבל את התמליל ופצל אותו למקטעים קצרים (תורי דיבור ומשפטים).
    2. קודד כל מקטע תוך הבנת ההקשר המלא של הפגישה.
    3. חוק ה-Ex-room: אם המקטע מתאר אירוע חיצוני, דיווח על העבר, או צד ג' - החזר תמיד NONE.
    4. חוק השאלות: שאלות החזר NONE.
    5. אם המקטע הוא "כאן ועכשיו" בחדר, החזר קוד של 3 אותיות:
       - דובר: מ/ל
       - מוקד: מ/ל/ד
       - ממד: ר/ת/ס
       
    חשוב מאוד: אל תכתוב שום טקסט, הקדמה או סיכום. החזר אך ורק רשימת JSON חוקית הבנויה כמערך של מערכים (רשימה של רשימות). ללא מפתחות כלל, רק ערכים לפי הסדר הזה: [טקסט המקטע, קוד, הסבר].
    דוגמה:
    [
      ["זה מקטע מהתמליל", "מ-מ-ת", "זה הסבר הקידוד"]
    ]
    """
    
    try:
        response = model.generate_content(system_prompt + "\n\nהתמליל:\n" + transcript)
        raw_text = response.text
        
        # חילוץ ה-JSON
        match = re.search(r'\[.*\]', raw_text, re.DOTALL)
        if match:
            json_str = match.group(0)
        else:
            json_str = raw_text
            
        data = json.loads(json_str.strip())
        
        # יצירת טבלה מהנתונים הגולמיים
        df = pd.DataFrame(data)
        
        if not df.empty:
            # כפייה אגרסיבית של שמות העמודות, בלי קשר למה שה-AI יצר
            num_cols = len(df.columns)
            target_cols = ["מקטע מהתמליל", "קוד MATRIX", "הסבר הקידוד"]
            
            if num_cols >= 3:
                df = df.iloc[:, :3]
                df.columns = target_cols
            else:
                df.columns = target_cols[:num_cols]
                
        return df
        
    except json.JSONDecodeError:
        st.error("ה-AI החזיר תשובה שלא תואמת למבנה הנדרש. התשובה הגולמית:")
        st.code(raw_text)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"שגיאה כללית בניתוח: {e}")
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
                st.table(df) # מציג את הטבלה ללא
