from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
	app_name: str = Field(default="AI Customer Support Bot")
	database_url: str = Field(default="sqlite:////tmp/app.db")
	retriever_top_k: int = Field(default=5)
	escalation_threshold: float = Field(default=0.45)
	summary_after_messages: int = Field(default=12)

	# Hugging Face (kept but not used when OpenRouter configured)
	hf_api_key: str | None = Field(default=None, alias="HUGGINGFACE_API_KEY")
	hf_model_name: str = Field(default="huggingfaceh4/zephyr-7b-beta", alias="HF_MODEL_NAME")

	# OpenRouter
	openrouter_api_key: str | None = Field(default=None, alias="OPENROUTER_API_KEY")
	openrouter_model_name: str = Field(default="meta-llama/llama-3.1-8b-instruct", alias="OR_MODEL_NAME")
	openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1", alias="OR_BASE_URL")

	# Pydantic v2 config
	model_config = SettingsConfigDict(
		protected_namespaces=("settings_",),
		env_file=".env",
		env_file_encoding="utf-8",
	)


settings = Settings()
