import sqlite3
import csv
import io

class DBManager:
    def __init__(self, db_name="ctsd_memory.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()
        
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS papers 
                          (id INTEGER PRIMARY KEY, title TEXT, abstract TEXT, source TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS hypotheses 
                          (id INTEGER PRIMARY KEY, content TEXT, verdict TEXT, score REAL)''')
        self.conn.commit()
        
    def insert_paper(self, title, abstract, source):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO papers (title, abstract, source) VALUES (?, ?, ?)", 
                       (title, abstract, source))
        self.conn.commit()
        
    def insert_hypothesis(self, content, verdict, score):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO hypotheses (content, verdict, score) VALUES (?, ?, ?)", 
                       (content, verdict, score))
        self.conn.commit()

    def get_approved_hypotheses(self, limit=3):
        cursor = self.conn.cursor()
        cursor.execute("SELECT content FROM hypotheses WHERE verdict LIKE '%Approved%' ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        return [row[0] for row in rows]

    def get_all_approved_hypotheses(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT content FROM hypotheses WHERE verdict LIKE '%Approved%'")
        rows = cursor.fetchall()
        return [row[0] for row in rows]

    def get_success_rate(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM hypotheses")
        total = cursor.fetchone()[0]
        if total == 0: return 1.0 # Default to 100% success rate if no data exists
        cursor.execute("SELECT COUNT(*) FROM hypotheses WHERE verdict LIKE '%Approved%'")
        approved = cursor.fetchone()[0]
        return approved / total
        
    def clear_memory(self):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM papers")
        cursor.execute("DELETE FROM hypotheses")
        self.conn.commit()

    def export_hypotheses_to_csv(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, content, verdict, score FROM hypotheses")
        rows = cursor.fetchall()
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Content', 'Verdict', 'Score'])
        writer.writerows(rows)
        return output.getvalue()

    def export_papers_to_csv(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, title, abstract, source FROM papers")
        rows = cursor.fetchall()
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Title', 'Abstract', 'Source'])
        writer.writerows(rows)
        return output.getvalue()
