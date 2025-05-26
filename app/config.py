from pydantic import computed_field, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_NAME: str = Field(default='name')
    DATABASE_USER: str = Field(default='user')
    DATABASE_PASSWORD: str = Field(default='password')
    DATABASE_HOST: str = Field(default='localhost')
    DATABASE_PORT: str = Field(default='5432')

    SECRET_KEY: str = Field(default="your-secret-key",)
    CLIENT_ID: str = Field(default='your-client-id')
    CLIENT_SECRET_KEY: str = Field(default='your-client-secret-key')

    AUTHORIZE_URL: str = Field(default='http://localhost:80/oauth/authorize/',)
    ACCESS_TOKEN_URL: str = Field(default='http://localhost:80/oauth/token/',)
    REVOKE_TOKEN_URL: str = Field(default='http://localhost:80/oauth/revoke_token/')
    USERINFO_URL: str = Field(default='http://localhost:80/api/auth/userinfo/',)

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@" \
               f"{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

    model_config = SettingsConfigDict(env_file='.env')

settings = Settings()
