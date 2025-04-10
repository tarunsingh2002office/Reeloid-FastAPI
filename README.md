# Reeloid Python Django Backend

Reeloid is a **Django-based backend** designed to support the Reeloid app. It provides REST APIs, authentication, Celery task management, and database operations using MongoDB and MySQL.

---

## 🚀 Features

- ✅ **Django REST Framework (DRF)** for API development
- ✅ **MongoDB ** database support
- ✅ **Celery** for asynchronous task execution
- ✅ **Redis** for caching and task queueing
- ✅ **Google Authentication** for secure login
- ✅ **MoviePy** for video processing
- ✅ **SpeechRecognition** for audio handling
- ✅ **Cron Jobs** with Celery Beat for scheduled tasks

---

## 🛠️ Installation Guide (Windows, Ubuntu/Linux, macOS)

### **1️⃣ Clone the Repository**
Run the following command in **CMD (Windows)** or **Terminal (Linux/macOS)**:
```sh
git clone https://github.com/yourusername/reeloid-python-django-backend.git
cd reeloid-python-django-backend
```

### **2️⃣ Create a Virtual Environment**
- **For Windows (CMD or PowerShell)**:
  ```sh
  python -m venv venv
  venv\Scripts\activate
  ```
- **For Ubuntu/Linux/macOS**:
  ```sh
  python3 -m venv venv
  source venv/bin/activate
  ```

### **3️⃣ Install Dependencies**
```sh
pip install -r requirements.txt
```

### **4️⃣ Set Up Environment Variables**
Create a `.env` file in the project root and add:
```env
SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=connection string for mongo db
MONGO_URI=connection string for mongo db
REDIS_URL=redis://localhost:6379
```

### **5️⃣ Apply Migrations**
Run the following command:
```sh
python manage.py migrate
```

### **6️⃣ Run the Development Server**
```sh
python manage.py runserver
```
Your backend should now be running at **`http://127.0.0.1:8000/`** 🎉

---

## ⚡ **Celery & Redis Setup (Task Queue Management)**

### **1️⃣ Start Redis Server**
Ensure Redis is running before starting Celery:
- **On Ubuntu/Linux/macOS**:
  ```sh
  sudo systemctl start redis
  ```
- **On Windows (Using WSL or Redis for Windows)**:
  ```sh
  redis-server
  ```

### **2️⃣ Start Celery Workers**
#### 🔹 **Run a Single Worker**
- **For Ubuntu/Linux/macOS**:
  ```sh
  celery -A reeloid_backend worker --loglevel=info
  ```
- **For Windows** (since multi-threading is not well-supported, use `--pool=solo`):
  ```sh
  celery -A reeloid_backend worker --loglevel=info --pool=solo
  ```

#### 🔹 **Run Celery with Multiple Workers (Concurrency)**
- **For Ubuntu/Linux/macOS**:
  ```sh
  celery -A reeloid_backend worker --loglevel=info --concurrency=4
  ```
- **For Windows**:
  ```sh
  celery -A reeloid_backend worker --loglevel=info --pool=solo --concurrency=2
  ```

### **3️⃣ Start Celery Beat (for Scheduled Tasks)**
```sh
celery -A reeloid_backend beat --loglevel=info
```

### **4️⃣ Start Celery Flower (Task Monitoring)(skippable)**
To monitor Celery tasks via a **web interface**, install **Flower** and run:
```sh
pip install flower
celery -A reeloid_backend flower
```
Access Flower at: **`http://localhost:5555`**

---

## 🔥 API Endpoints

| Method | Endpoint | Description |
|--------|---------|-------------|
| `GET`  | `/api/users/` | Retrieve all users |
| `POST` | `/api/users/` | Create a new user |
| `GET`  | `/api/tasks/` | Retrieve assigned check-in tasks |
| `POST` | `/api/tasks/complete/` | Mark a task as completed |

For more details, check out the **Swagger API Docs**:
```sh
http://127.0.0.1:8000/swagger/
```

---

## 📜 Dependencies

Here are the key Python libraries used in this project:

- **Django** `5.1.1` – Web framework
- **Django REST Framework** `3.15.2` – API handling
- **Celery** `5.4.0` – Asynchronous task queue
- **Redis** `5.2.1` – Background task broker
- **MongoEngine** `0.29.0` – MongoDB ORM
- **MySQLclient** `2.2.4` – MySQL database support
- **MoviePy** `1.0.3` – Video processing
- **SpeechRecognition** `3.10.4` – Audio processing
- **Google AI API** `0.8.2` – AI-powered functionality

> **Full dependencies list is available in** `requirements.txt`.

---

## 🤝 Contributing

We welcome contributions! Follow these steps:

1. **Fork** the repository.
2. **Create a branch** (`git checkout -b feature-branch`).
3. **Commit your changes** (`git commit -m "Added new feature"`).
4. **Push to your branch** (`git push origin feature-branch`).
5. **Create a Pull Request**.

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 📞 Contact

- **GitHub:** [@shivam5676](https://github.com/shivam5676)
- **Email:** shivam.handler@gmail.com

---
🚀 **Happy Coding!**

