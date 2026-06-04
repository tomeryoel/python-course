# PTSD Companion

עוזר דיגיטלי אישי לזיכרון טיפולי, עומס קוגניטיבי ומצבי מצוקה — מבוסס RAG על Amazon Bedrock Knowledge Base.

## מטרת הפרויקט

לאחר ביקור אצל פסיכולוג, פסיכיאטר או מטפל, מטופלים רבים מתקשים לזכור הנחיות, תזמון תרופות, כלי קרקוע ומשימות יומיות — במיוחד תחת סטרס.

**PTSD Companion** משמש "מוח חיצוני": שולף מידע מהמסמכים שהועלו, מציג משימות מעשיות ב-`tasks.json`, ועונה בעברית בטון רגוע ומעשי.

> **הצהרה:** המערכת אינה מחליפה ייעוץ רפואי, פסיכיאטרי או פסיכולוגי. היא מציגה מידע על בסיס המסמכים שהועלו בלבד.

---

## נושא ומאגר מסמכים

- **נושא:** ליווי מטופל עם PTSD / עומס קוגניטיבי / קשיי זיכרון טיפולי.
- **6 מסמכים מדומים בעברית** (שמות ורישיונות פיקטיביים):
  - 3× DOCX — סיכומי פסיכולוגיה (CBT, EMDR, קרקוע, עוגנים)
  - 3× PDF — סיכומי פסיכיאטריה (תרופות, שינה, SOS)
- תמיכה עתידית במסמכים באנגלית — תשובות בעברית כברירת מחדל.

---

## ארכיטקטורה

```text
Documents (S3)
    ↓
Amazon Bedrock Knowledge Base
    ↓
Flask + boto3 (retrieve + converse)
    ↓
React UI + tasks.json
    ↓
Docker → EC2 (גישה ציבורית לבדיקה)
```

### זרימות מידע

1. **קלט:** הדבקת סיכום קליני → `/api/extract-tasks` → משימות ב-`tasks.json`
2. **פלט:** שאלה בצ'אט → שליפה מ-KB + משימות פתוחות → תשובה בעברית

---

## שירותי AWS

| שירות | שימוש |
|--------|--------|
| Bedrock Knowledge Base | אחסון ושליפת מסמכים |
| bedrock-agent-runtime | `retrieve()` |
| bedrock-runtime | `converse()` (Amazon Nova מומלץ) |
| S3 | מקור מסמכים ל-KB |
| EC2 | פריסת דמו ציבורי |

---

## התקנה מקומית

### דרישות

- Python 3.11+
- Node.js 18+ (לבניית React)
- חשבון AWS עם KB מסונכרן

### 1. משתני סביבה

```bash
cp .env.example .env
```

מלא: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `KNOWLEDGE_BASE_ID`, `BEDROCK_MODEL_ID=amazon.nova-lite-v1:0`

### 2. Backend

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 3. בדיקת RAG

```bash
python rag_engine.py
```

### 4. Frontend

```bash
cd frontend
npm install
npm run build
cd ..
```

### 5. הרצת האפליקציה

```bash
python app.py
```

פתח: http://127.0.0.1:5000

פיתוח React נפרד (עם proxy):

```bash
cd frontend && npm run dev
```

---

## API

| Method | Path | תיאור |
|--------|------|--------|
| GET | `/health` | סטטוס |
| POST | `/api/chat` | `{"question": "..."}` |
| GET/POST | `/api/tasks` | רשימה / הוספה |
| PATCH/DELETE | `/api/tasks/<id>` | עדכון / מחיקה |
| POST | `/api/extract-tasks` | `document_text`, `source_name` |
| POST | `/api/clear` | ניקוי זיכרון שיחה |

---

## Docker

```bash
docker build -t ptsd-companion .
docker run -p 5000:5000 --env-file .env ptsd-companion
```

---

## פריסה ל-EC2

1. הפעל EC2 (Amazon Linux / Ubuntu).
2. התקן Docker.
3. העתק את הפרויקט או `git clone`.
4. צור `.env` על השרת (ללא commit).
5. `docker build` + `docker run -p 5000:5000 --env-file .env`
6. Security Group: פתח פורט **5000** (או 80 עם nginx).
7. בדוק: `http://<PUBLIC_IP>:5000`
8. צלם screenshots לגמר.
9. **מחק** EC2, KB זמני, buckets בדיקה — למנוע עלויות.

רשום ב-README את ה-IP/URL שבו בדקת.

---

## בדיקות אוטומטיות

```bash
pytest
```

(ללא קריאות AWS אמיתיות — עם mocking)

---

## שאלות לדוגמה לבדיקה ידנית

- מהם הסימפטומים המרכזיים של המטופל לפי המסמכים?
- מה עושים בזמן טריגר של רעש חזק?
- אני בסטרס עכשיו, מה לעשות?
- מתי לקחת ציפרלקס? מה הקלונקס?

תרחישים A–E מוגדרים בממשק השיחה.

---

## רשימת Screenshots לגמר

- [ ] Bedrock Knowledge Base בקונסול
- [ ] Data source מסונכרן
- [ ] `python rag_engine.py` מקומי
- [ ] Flask / React מקומי
- [ ] `docker run` עובד
- [ ] EC2 instance
- [ ] אפליקציה נגישה ב-IP ציבורי
- [ ] לפחות שאלה ותשובה אחת מוצלחת

---

## ניקוי AWS (חובה אחרי הגשה)

מחק או השבת:

- EC2 instance
- Elastic IP (אם הוקצה)
- Knowledge Base / data source (אם נוצר לבדיקות בלבד)
- S3 buckets זמניים

זה מונע חיובים מיותרים.

---

## מבנה פרויקט

```text
app.py              # Flask API + SPA
rag_engine.py       # Bedrock RAG
tasks.py / tasks.json
memory.py           # SQLite שיחה
frontend/           # React (Vite)
static/dist/        # build output
tests/
Dockerfile
.env.example
data/               # מסמכי דמו (מקור ל-KB)
```

---

## רישיון / שימוש

פרויקט סטודנטיאלי — מסמכים פיקטיביים. לא לשימוש קליני.
