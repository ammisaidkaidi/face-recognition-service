# Face Recognition Backend

Standalone FastAPI service for enrollment, recognition, landmarks, and canonical head pose. It identifies **only** people enrolled in this application's SQLite database. The model layer is isolated behind `VisionEngine`; the production adapter is InsightFace/ONNX Runtime (CPU), while a deterministic fake is used only by automated tests.

> Face embeddings are sensitive biometric data. Obtain consent, define retention periods, restrict access, and follow applicable law. This baseline does not implement liveness detection and must not be used as the sole control for high-risk access decisions.

## Quick start

Requires Python 3.11+.

```bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -e '.[insightface,test]'
cp .env.example .env
./scripts/run.sh
```

The first InsightFace startup downloads the configured model pack into `MODEL_ROOT` if absent. In restricted environments, provision the model files there ahead of time. OpenAPI is at `http://localhost:8000/docs` in non-production environments.

For a lightweight contract-only local run, set `VISION_BACKEND=fake`. It is deterministic and **not a real recognition model**.

## Architecture

```text
API -> application services -> domain -> model/repository adapters -> SQLite/ONNX
```

Domain dataclasses import neither FastAPI nor SQLite. Model-specific code is confined to `app/services/adapters`. Repositories isolate persistence, making a later PostgreSQL/pgvector implementation possible without changing API contracts.

## REST API

All management routes may require `X-API-Key` when `API_KEY` is configured.

- `GET /api/v1/health`
- `POST /api/v1/people` — body `{"name":"John Doe"}`
- `GET /api/v1/people`
- `GET /api/v1/people/{person_id}`
- `DELETE /api/v1/people/{person_id}` — soft-deactivates the person and deletes biometric samples
- `POST /api/v1/people/{person_id}/enrollment`

## WebSocket protocol

### Enrollment: `/ws/v1/enrollment/{session_id}`

Send one binary JPEG or WebP per message. Responses contain `accepted`, stable `reason`, `state`, `accepted_samples`, `required_samples`, and `pose_bucket`. Rejection codes include `FACE_NOT_FOUND`, `MULTIPLE_FACES`, `FACE_TOO_SMALL`, `LOW_QUALITY`, `BAD_BRIGHTNESS`, `EXTREME_POSE`, and `DUPLICATE_POSE`. A session completes at `ENROLLMENT_MIN_SAMPLES` accepted, sufficiently distinct poses.

### Identify: `/ws/v1/identify`

Send binary JPEG/WebP messages. Every response has `type`, Unix `timestamp`, and `faces`. Each face is `known` only when cosine distance is at or below `RECOGNITION_THRESHOLD`; otherwise it is `unknown`. No nearest identity is forced.

Canonical pose is degrees:

- `yaw`: left/right rotation; negative is left, positive is right
- `pitch`: up/down rotation; negative is up, positive is down
- `roll`: in-plane tilt; negative counter-clockwise, positive clockwise
- `rotation`: frontend convenience mapping `{x: pitch, y: yaw, z: roll}`

Verify signs against your chosen model/version and camera mirroring before production deployment.

## Configuration and threshold calibration

Every setting is documented in `.env.example`. Important controls:

- `RECOGNITION_THRESHOLD`: cosine-distance match cutoff. **Must be calibrated** on representative validation data; lower values are stricter.
- `MIN_FACE_SIZE`: minimum bbox side in pixels.
- `MIN_SHARPNESS`: minimum Laplacian variance.
- `MIN_BRIGHTNESS` / `MAX_BRIGHTNESS`: accepted grayscale mean.
- `MAX_ABS_YAW` / `MAX_ABS_PITCH`: enrollment/recognition pose quality limits.
- `POSE_DIVERSITY_DEGREES`: separation from previously accepted enrollment poses.
- `PROCESS_FPS`: server-side WebSocket processing ceiling per connection.
- `MAX_FRAME_BYTES`: hard payload limit.
- `ENROLLMENT_MIN_SAMPLES` / `ENROLLMENT_MAX_SAMPLES`: enrollment limits (the initial flow auto-completes at the minimum).
- `MODEL_NAME`, `MODEL_VERSION`, `MODEL_ROOT`, `ONNX_PROVIDERS`: model identity and runtime.
- `CORS_ORIGINS`: comma-separated explicit browser origins.
- `API_KEY`: optional baseline management API protection; use a real identity provider/gateway in production.

Embeddings are matched only where model name, version, and dimension are compatible. Changing a model/version requires re-enrollment or an explicit migration.

## Testing

```bash
pip install -e '.[test]'
pytest
```

Tests cover health, person lifecycle/deletion, API-key protection, enrollment, known recognition, malformed frames, embedding serialization/model compatibility, distance thresholds, and temporal smoothing. `FakeVisionEngine` avoids downloading models in CI. Add consented, licensed vision fixtures and measured false-accept/false-reject tests before release.

## Privacy, logging, and retention

Raw frames are decoded in memory and not persisted. `RETAIN_IMAGES` is reserved and defaults false. Logs contain request IDs, operation, status, and timing—not images, embeddings, or secrets. Deactivation deletes face samples while retaining the inactive person record. Encrypt storage/backups, put TLS and authentication in front of both HTTP and WebSocket traffic, and establish deletion/export/audit procedures before production.

## Production deployment

Use the included Dockerfile or a pinned deployment build. Pre-provision models, mount encrypted persistent storage for `data/`, set `APP_ENV=production`, configure strict origins and `API_KEY`, terminate TLS at a trusted proxy, cap connections/request rates there, and run one worker per loaded model unless memory sizing proves otherwise. SQLite is appropriate for a single instance; migrate to PostgreSQL for multi-instance writes. Health endpoint readiness currently confirms initialization because model loading occurs during startup.

## Current scope

Implemented: person management, enrollment sessions, quality checks, pose diversity, multiple embeddings/person, model compatibility, binary WebSockets, thresholded matching, pose/landmark payloads, structured HTTP logs, limits, CORS, API-key option, and tests.

Not implemented by design: frontend, liveness/anti-spoofing, photorealistic 3D reconstruction, tracking, GPU orchestration, pgvector, encrypted embedding fields, or an external identity provider.
