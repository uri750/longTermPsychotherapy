import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import re

# 1. הכנס את המפתח שלך בין המרכאות:
API_KEY = "AIzaSyD2EKvLQEns8YXxiZrxz1GGAgIHqfdVQXk" 

def analyze_transcript(transcript):
    clean_key = API_KEY.strip()
    genai.configure(api_key=clean_key)
    
    # --- מנגנון אוטומטי למציאת מודל תקין ומהיר ---
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if not available_models:
            st.error("לא נמצאו מודלים מאושרים למפתח שלך בשרתי גוגל.")
            return pd.DataFrame()
            
        chosen_model_name = available_models[0]
        
        # מחפש את מודל הפלאש המהיר שאינו חסום
        for name in available_models:
            if 'flash' in name:
                chosen_model_name = name
                break
                
        model = genai.GenerativeModel(chosen_model_name)
    except Exception as setup_error:
        st.error(f"שגיאה בהתחברות לשרתי גוגל: {setup_error}")
        return pd.DataFrame()
    
    prompt = f"""
    אתה מומחה קליני בקידוד תמלילי פסיכותרפיה לפי מודל MATRIX (Mendlovic et al., 2017).
    
    כדי לקודד במדויק, עליך לפעול לפי השלבים הבאים:
    
    שלב 1: פיצול אגרסיבי (Fragmentation) - קריטי!
    אסור לך לקודד תור דיבור שלם כמקשה אחת אם יש בו שינוי נושא. עליך לפצל כל תור דיבור למקטעים קצרים (משפטים או חלקי משפטים) בכל פעם שיש מעבר בין דיבור על העבר/מחוץ לחדר (Ex-room) לבין חוויה שקורית עכשיו בחדר (כאן ועכשיו), או כשמתחלף נושא. 
    לדוגמה: "אני תמיד מאחר" (יפוצל למקטע 1) | "ואני רואה שזה מכעיס אותך עכשיו" (יפוצל למקטע 2).
    
    שלב 2: סינון Ex-room ושאלות
    עבור כל תת-מקטע שפיצלת: אם הוא מתאר אירוע שקרה מחוץ לחדר, תבניות כלליות מחוץ לטיפול, דיווח על העבר, מתייחס לצד שלישי, או שהוא מנוסח כשאלה - החזר תמיד את הקוד NONE.
    
    שלב 3: זיהוי וקידוד "כאן ועכשיו"
    אם תת-המקטע עוסק במה שקורה כעת בחדר בין המטפל למטופל, הרכב קוד של 3 אותיות באנגלית המופרדות במקף (למשל T-P-C) לפי הלוגיקה הבאה:
    
    אות ראשונה - הדובר:
    - 'T': המטפל (Therapist).
    - 'P': המטופל (Patient).
    
    אות שנייה - המוקד:
    - 'T': המוקד הוא המטפל.
    - 'P': המוקד הוא המטופל.
    - 'D': המוקד הוא הדיאדה (היחסים, הקשר).
    
    אות שלישית - הממד:
    - 'S': מרחב (Space - הפוטנציאל לחוות. למשל "אני חסום", "ריק לי").
    - 'C': תוכן (Content - החוויה עצמה: רגש, מחשבה, או פעולה בחדר כמו בכי, למשל "אני עצוב", "אני לא יודע [למה אני בוכה]").
    - 'O': סדר (Order - ספקות, דילמות פנימיות, קונפליקט).
    
    התמליל לניתוח:
    {transcript}
    
    עליך להחזיר אך ורק מערך JSON נקי, ללא טקסט מקדים. 
    לכל אובייקט יהיו בדיוק 3 המפתחות הבאים באנגלית:
    "text" (תת-המקטע המדויק שפיצלת), "code" (הקוד או NONE), "explanation" (הסבר מדוע בחרת בקוד או מדוע זה NONE).
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
            df = df.iloc[:, :3] 
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
