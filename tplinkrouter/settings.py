from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
from typing import Optional, Literal


class ConnectionSettings(BaseModel):
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        cli_parse_args=True, 
        cli_prog_name="tplinkrouter2mqtt",
        )

    tplink: ConnectionSettings
    mqtt: ConnectionSettings
    log_level: Literal['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'] = "INFO"
    delay_before_reconnection: int = 5
