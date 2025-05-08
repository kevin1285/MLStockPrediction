# MLStockPrediction

## Tech Stack
### Frontend
- Vue.js 3
- Vite

### Backend
- FastAPI (Python 3.10+)
- TensorFlow / Keras (for ML inference)
- Polygon.io API (for market data)

## Running Locally
### Backend 
```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables (e.g. POLYGON_API_KEY)

# Run the FastAPI server
uvicorn main:app --reload
```

### Frontend
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
