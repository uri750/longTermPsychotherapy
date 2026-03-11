import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import re

# כאן תצטרך להכניס את מפתח ה-API שלך
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
       
    חשוב מאוד: אל תכתוב שום טקסט, הקדמה או סיכום. החזר אך ורק רשימת JSON חוקית שבה המפתחות הם אך ורק באנגלית:
    [
      {"fragment": "טקסט המקטע בעברית", "code": "מ-מ-ת או NONE", "explanation": "הסבר הקידוד בעברית"}
    ]
    """
    
    try:
        response = model.generate_content(system_prompt + "\n\nהתמליל:\n" + transcript)
        raw_text = response.text
        
        # חילוץ ה-JSON למקרה שהמודל מוסיף טקסט מיותר
        match = re.search(r'\[.*\]', raw_text, re.DOTALL)
        if match:
            json_str = match.group(0)
        else:
            json_str = raw_text
            
        data = json.loads(json_str.strip())
        df = pd.DataFrame(data)
        
        # תרגום בטוח של כותרות העמודות לעברית
        rename_dict = {
            "fragment": "מקטע מהתמליל",
            "code": "קוד MATRIX",
            "explanation": "הסבר הקידוד"
        }
        df = df.rename(columns=rename_dict)
        
        # סינון בטוח: מציג רק עמודות שבאמת קיימות כדי למנוע קריסת KeyError
        available_columns = [col for col in ["מקטע מהתמליל", "קוד MATRIX", "הסבר הקידוד"] if col in df.columns]
        
        return df[available_columns]
        
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
    if API_KEY ==
