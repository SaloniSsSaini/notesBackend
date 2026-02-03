# Clean Advanced Notes API

A clean and advanced backend API for managing notes, built using **FastAPI** and **SQLite**.  
This project goes beyond basic CRUD and demonstrates real-world backend concepts in a **minimal and readable structure**.

---

## 🚀 Features

### Core Features
- Create, update, delete, and list notes
- Input validation (required fields, trimmed values)
- Partial updates
- Notes sorted by most recently updated

### Advanced Features
- API key–based authentication (via request headers)
- Rate limiting (max 5 note creations per minute)
- Pagination and sorting
- Soft delete (notes are not permanently removed)
- Advanced search with relevance ranking
- Search result caching
- Analytics / stats endpoint

---

## 🛠 Tech Stack

- **FastAPI** – Backend framework
- **SQLite** – Lightweight database
- **SQLAlchemy** – ORM
- **Pydantic** – Data validation
- **Uvicorn** – ASGI server

---

## 📁 Project Structure

notes_backend/
│
├── main.py # Main application (routes + logic)
├── database.py # Database connection
├── models.py # SQLAlchemy models
├── schemas.py # Pydantic schemas
├── requirements.txt
├── README.md
└── .gitignore


> The structure is intentionally kept minimal for clarity and easy understanding.

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository
```bash
git clone https://github.com/SaloniSsSaini/notesBackend.git
cd notesBackend
2️⃣ Create and activate virtual environment
python -m venv venv
Windows:

venv\Scripts\activate
Mac/Linux:

source venv/bin/activate
3️⃣ Install dependencies
pip install -r requirements.txt
4️⃣ Run the server
uvicorn main:app --reload
📌 API Documentation
Swagger UI is available at:

http://127.0.0.1:8000/docs
🔐 Authentication
All APIs require an API key passed via request headers:

x-api-key: secret123
In Swagger:

Open any endpoint

Click Try it out

Enter secret123 in the x-api-key header field

🔗 API Endpoints
➕ Create Note
POST /api/v1/notes
📄 Get Notes (Pagination & Sorting)
GET /api/v1/notes
Query params:

page (default: 1)

limit (default: 10)

sort_by → created_at | updated_at | title

order → asc | desc

✏️ Update Note
PUT /api/v1/notes/{note_id}
🗑 Soft Delete Note
DELETE /api/v1/notes/{note_id}
🔍 Search Notes (Ranked)
GET /api/v1/notes/search?q=keyword
Case-insensitive

Partial matching

Ranked by relevance

📊 Notes Statistics
GET /api/v1/notes/stats
Returns:

Total notes

Notes created today

Last updated note ID

🧠 Design Notes
Soft delete is used instead of permanent deletion

Rate limiting and caching are implemented in-memory for simplicity

API versioning (/api/v1) is used for future compatibility

The project avoids over-engineering while demonstrating backend maturity

👩‍💻 Author
Saloni Saini
Backend Developer | Python | FastAPI
