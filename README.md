# Face Recognition Service & Web Console

A standalone, CPU-compatible face recognition platform with a FastAPI backend and React web console.

## Components

- [`backend/`](backend/) — FastAPI REST/WebSocket service, SQLite repositories, InsightFace/ONNX adapter, enrollment, recognition, landmarks, and head pose.
- [`frontend/`](frontend/) — Responsive Vite/React console for live identification, guided enrollment, identity management, and 3D-style pose visualization.

## Quick start

See the component documentation:

- [Backend setup and API](backend/README.md)
- [Frontend setup](frontend/README.md)

> Face embeddings are sensitive biometric data. Obtain consent, restrict access, define retention policies, and do not use this baseline as the sole control for high-risk decisions. Liveness detection is not included.
