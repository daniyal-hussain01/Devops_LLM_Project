import sqlite3

def get_prompt_by_id(prompt_id):
    conn = sqlite3.connect("prompts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT prompt FROM prompts WHERE id = ?", (prompt_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_all_prompts():
    conn = sqlite3.connect("prompts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM prompts")
    results = cursor.fetchall()
    conn.close()
    return results