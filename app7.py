import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import re

# 1. הכנס את המפתח שלך בין המרכאות:
API_KEY = "AIzaSyCPnwhOLk8_dVBkleCpjenGkBd5Yb_51yM" 

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
    
    שלב 1: פיצול אגרסיבי (Fragmentation)
    פצל כל תור דיבור למקטעים קצרים (משפטים/חלקי משפטים). חובה לפצל במיוחד במעברים בין סיפורי רקע מבחוץ (Ex-room) לבין התייחסות למטפל, לקשר הטיפולי או רגשות שעולים כעת.
    
    שלב 2: סינון Ex-room ושאלות - קרא היטב את החריגים!
    אם המקטע מתאר אירוע שקרה מחוץ לחדר, תבניות חיים כלליות, או שהוא שאלה - החזר תמיד NONE.
    *חריגים קריטיים (זה 'כאן ועכשיו' וחובה לקודד אותם, לא NONE!):*
    1. רפלקציה על הקשר הטיפולי והמניעים: כשהמטופל מנתח את ההתנהגות שלו כלפי המטפל בחדר ("אני מסכים שרציתי שתעריץ אותי") - זה תמיד מקודד! גם אם זה מתייחס לפגישה הקודמת.
    2. מחשבה/רגש בהווה: תיאור חוויה שמתרחשת עכשיו ("אני לא מבין עכשיו לאן הזמן עף").
    3. הבעות לא-מילוליות בחדר: בכי, תנועות גוף, השתהות.
    
    שלב 3: זיהוי וקידוד "כאן ועכשיו"
    למקטעים שאינם NONE, הרכב קוד של 3 אותיות באנגלית (למשל P-P-C):
    
    אות ראשונה - הדובר: 'T' (המטפל) או 'P' (המטופל).
    
    אות שנייה - המוקד:
    - 'T': המטפל (המטופל מדבר על תכונות המטפל).
    - 'P': המטופל (המטופל מנתח את מניעיו והתנהגותו, למשל "רציתי שתעריץ אותי", או כשהמטפל מתייחס למטופל).
    - 'D': דיאדה (רק חוויות משותפות וממוזגות לחלוטין - "שנינו").
    
    אות שלישית - הממד:
    - 'S': מרחב (Space - פוטנציאל לחוות. למשל "אני חסום").
    - 'C': תוכן (Content - החוויה עצמה: רגש, מחשבה, רפלקציה על מניעים, הבעה לא-מילולית).
    - 'O': סדר (Order - ספקות, דילמות פנימיות, קונפליקט מפורש).
    
    התמליל לניתוח:
    {transcript}
    
    החזר אך ורק מערך JSON נקי, ללא טקסט מקדים. 
    לכל אובייקט יהיו בדיוק 3 המפתחות:
    "text" (תת-המקטע שפיצלת), "code" (הקוד או NONE), "explanation" (הסבר קצר בעברית).
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
