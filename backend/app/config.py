from functools import lru_cache
from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")
    app_env: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    database_url: str = "sqlite:///./data/app.db"
    vision_backend: str = "insightface"
    model_name: str = "buffalo_l"
    model_root: Path = Path("./models")
    model_version: str = "insightface-buffalo_l-v1"
    onnx_providers: str = "CPUExecutionProvider"
    detection_size: int = 640
    recognition_threshold: float = Field(0.45, gt=0)
    min_face_size: int = Field(80, ge=16)
    min_sharpness: float = Field(60.0, ge=0)
    min_brightness: float = Field(35.0, ge=0, le=255)
    max_brightness: float = Field(225.0, ge=0, le=255)
    max_abs_yaw: float = Field(45.0, ge=0)
    max_abs_pitch: float = Field(35.0, ge=0)
    process_fps: float = Field(10.0, gt=0, le=60)
    max_frame_bytes: int = Field(2_000_000, gt=0)
    enrollment_min_samples: int = Field(5, ge=1)
    enrollment_max_samples: int = Field(20, ge=1)
    pose_diversity_degrees: float = Field(10.0, ge=0)
    stability_frames: int = Field(3, ge=1)
    unknown_hysteresis_frames: int = Field(2, ge=1)
    cors_origins: list[str] | str = ["http://localhost:3000"]
    retain_images: bool = False
    api_key: str | None = None
    log_level: str = "INFO"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value):
        return [x.strip() for x in value.split(",") if x.strip()] if isinstance(value, str) else value

    @property
    def providers(self) -> list[str]:
        return [x.strip() for x in self.onnx_providers.split(",") if x.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()
