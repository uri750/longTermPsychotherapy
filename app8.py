import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import re

# 1. הכנס את המפתח שלך בין המרכאות:
API_KEY = "AIzaSyAl3-Xmtt3YYzs3zT8IOZxdRtX03V3WOS0" 

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
    
    שלב 1: זיהוי דוברים, פיצול והורשה (Fragmentation)
    התמליל מסומן בקידומות: "אני:" (המטפל - T) ו-"הוא:" (המטופל - P).
    פצל כל תור דיבור למקטעים קצרים (משפטים/חלקי משפטים). חובה להוריש את הקידומת ("אני:" או "הוא:") לכל תת-מקטע שאתה יוצר מאותה פסקה כדי לשמור על זהות הדובר.
    
    שלב 2: סינון נוקשה (הכל מקבל NONE!)
    עליך להחזיר תמיד NONE במקרים הבאים:
    1. עבר ומחוץ לחדר (Ex-room): אירועים שקרו לפני הפגישה או בדרך אליה ("בדרך חשבתי", "הודעת לי שאתה חולה").
    2. שאלות: כל משפט המנוסח כשאלה ("התכוננת?", "למה זה?").
    3. תגובות ריקות: "אוקיי", "כן", "ממ-המ" שאינן מביעות חוויה/פעולה משמעותית.
    
    שלב 3: זיהוי וקידוד "כאן ועכשיו"
    רק למקטעים שמתרחשים *כרגע* בחדר, הרכב קוד של 3 אותיות:
    
    אות ראשונה - הדובר: 'T' (אני:) או 'P' (הוא:).
    
    אות שנייה - המוקד:
    - 'T': המטפל (המטופל מדבר על פעולות המטפל בחדר).
    - 'P': המטופל (המטופל מדבר על עצמו/מניעיו, למשל "רציתי שתעריץ").
    - 'D': דיאדה (רק חוויות משותפות ממוזגות לחלוטין).
    
    אות שלישית - הממד:
    - 'S': מרחב (Space - חוסר יכולת לחוות/למלל. למשל: "אני חסום", "לא מוצא מילים").
    - 'C': תוכן (Content - החוויה עצמה: רגש, מחשבה, תהייה נוכחית, הוראה פיזית בחדר).
    - 'O': סדר (Order - הגדרה נוקשה: קונפליקט מפורש, דילמה, משא ומתן בין חוויות, או שקילת חלופות. למשל: "מצד אחד... מצד שני", "אני מתלבט", "אני קרוע בין..."). 
    *חוק חשוב:* "אני לא מבין למה זה" ללא קונפליקט מפורש יקודד כתוכן (C) ולא כסדר (O).
    
    התמליל לניתוח:
    {transcript}
    
    החזר אך ורק מערך JSON נקי, ללא טקסט מקדים. 
    לכל אובייקט יהיו בדיוק 3 המפתחות:
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
