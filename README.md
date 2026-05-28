# 🌤️ Weather API

A RESTful API Gateway built with **FastAPI** that fetches real-time weather data from [Visual Crossing](https://www.visualcrossing.com/weather-api), caches responses with **Redis**, and protects endpoints with **rate limiting**.

Built as part of the [roadmap.sh](https://roadmap.sh) backend beginner projects.

---

## 🚀 Stack

- **Python 3.13**
- **FastAPI**
- **Pydantic v2**
- **httpx** — HTTP requests to Visual Crossing
- **Redis** (via Docker) — response caching
- **SlowAPI** — rate limiting
- **Scalar** — API documentation

---

## ⚙️ How it works

```
User → Weather API → (cached?) → Yes: return from Redis
                               → No: call Visual Crossing → save to Redis → return
```

- First request to a city calls Visual Crossing and caches the response for **30 minutes**
- Subsequent requests for the same city are served directly from Redis
- Each IP is limited to **10 requests per minute**

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/SantiagoGuzmanCastano/roadmap.sh-beginner-weather-api
cd roadmap.sh-beginner-weather-api

# Create virtual environment
python -m venv venv --without-pip
venv\Scripts\activate

# Install dependencies
pip install fastapi[standard] httpx redis slowapi scalar-fastapi python-dotenv
```

---

## 🔑 Environment variables

Create a `.env` file in the root of the project:

```
VISUAL_CROSSING_API_KEY=your_api_key_here
```

Get your free API key at [visualcrossing.com](https://www.visualcrossing.com/weather-api).

---

## 🐳 Redis with Docker

```bash
# Start Redis container
docker run -d --name redis -p 6379:6379 redis

# Stop
docker stop redis

# Start again
docker start redis
```

---

## ▶️ Running the server

```bash
fastapi dev main.py
```

API available at `http://localhost:8000`  
Documentation at `http://localhost:8000/docs`

---

## 📋 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/weather/{address}` | Get current weather for a city |
| `GET` | `/cached_weather_keys` | List all cities currently in cache |

---

## 🌡️ Weather Response

```json
{
  "address": "Barranquilla",
  "temp": 33.0,
  "tempmax": 33.4,
  "tempmin": 26.0,
  "feelslike": 40.6,
  "humidity": 62.8,
  "windspeed": 9.4,
  "winddir": 77,
  "conditions": "Partially cloudy"
}
```

---

## 📁 Project Structure

```
weather-api/
├── main.py        # FastAPI app, endpoints, Redis and rate limiting setup
├── schemas.py     # Pydantic models
├── .env           # Environment variables (not included in repo)
└── README.md
```

---

## ⚠️ Error handling

| Situation | Status Code |
|-----------|-------------|
| City not found | `404 Not Found` |
| Rate limit exceeded | `429 Too Many Requests` |
