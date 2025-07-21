import shutil
import os
import sys

def copy_project_to_english_path():
    """מעתיק את הפרויקט לתיקייה עם שם באנגלית בלבד"""
    
    # נתיב נוכחי
    current_path = os.getcwd()
    print(f"נתיב נוכחי: {current_path}")
    
    # יוצר נתיב חדש באנגלית בלבד
    # עולה רמה אחת למעלה ויוצר תיקייה חדשה
    parent_dir = os.path.dirname(current_path)
    new_project_path = os.path.join(parent_dir, "chess_project_english")
    
    print(f"נתיב חדש: {new_project_path}")
    
    try:
        # אם התיקייה קיימת, מוחק אותה
        if os.path.exists(new_project_path):
            print("מוחק תיקייה קיימת...")
            shutil.rmtree(new_project_path)
        
        # מעתיק את כל התיקייה
        print("מעתיק קבצים...")
        shutil.copytree(current_path, new_project_path)
        
        print(f"✅ הפרויקט הועתק בהצלחה!")
        print(f"📁 הנתיב החדש: {new_project_path}")
        print("\n🔧 כדי להמשיך לעבוד:")
        print("1. פתח terminal/cmd חדש")
        print(f"2. הכנס לתיקייה: cd \"{new_project_path}\"")
        print("3. הרץ: python main.py")
        
        return new_project_path
        
    except Exception as e:
        print(f"❌ שגיאה בהעתקה: {e}")
        return None

def create_simple_run_script():
    """יוצר קובץ הרצה פשוט"""
    script_content = """@echo off
echo Starting Kung Fu Chess...
cd /d "%~dp0"
python main.py
pause
"""
    
    with open("run_game.bat", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print("✅ נוצר קובץ run_game.bat - תוכל להקליק עליו כדי להריץ את המשחק")

if __name__ == "__main__":
    print("🥋 מעתיק פרויקט Kung Fu Chess לנתיב באנגלית...")
    print("=" * 50)
    
    new_path = copy_project_to_english_path()
    
    if new_path:
        # יוצר קובץ bat להרצה קלה
        current_dir = os.getcwd()
        os.chdir(new_path)
        create_simple_run_script()
        os.chdir(current_dir)
        
        print("\n" + "=" * 50)
        print("🎯 ההעתקה הושלמה!")
        print("כעת עבור לתיקייה החדשה והרץ את המשחק")