# Simple Flask API

A basic Flask API with health check endpoints.

## Setup

1. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python app.py
   ```

## Endpoints

- `GET /api/health`: Health check endpoint
- `GET /api/hello`: Returns a hello message

```

## Production Deployment

For production, use Gunicorn:

```

gunicorn -w 4 -b 0.0.0.0:5000 app:app

```

```
