# Persona Vision Webapp

React/Vite client for the Face Recognition Backend. It contains:

- live identification with face boxes, confidence, and a responsive 3D-style pose avatar;
- guided person creation and enrollment with quality-rejection feedback;
- enrolled-person management and biometric deletion;
- backend/model health status;
- binary JPEG WebSocket streaming (no base64).

## Run

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Start the backend on port 8000 first. Add `http://localhost:5173` to backend `CORS_ORIGINS`:

```env
CORS_ORIGINS=http://localhost:5173
```

Configuration:

- `VITE_API_BASE`: backend HTTP origin.
- `VITE_API_KEY`: optional management API key matching backend `API_KEY`.
- `VITE_CAPTURE_FPS`: client capture ceiling (defaults to 8).

Camera access requires localhost or HTTPS. No frames are stored by this client. The frontend mirrors camera video visually; coordinates are mirrored with the overlay so backend bounding boxes stay aligned.
