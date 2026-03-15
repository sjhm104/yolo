from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	"""全局配置对象，统一管理项目运行参数与环境变量读取。"""

	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
		extra="ignore",
	)

	PROJECT_NAME: str = "CampusWasteDetection"
	SQLALCHEMY_DATABASE_URI: str = (
		"mysql+pymysql://root:123456@localhost:3306/campus_waste_db"
	)


settings = Settings()
