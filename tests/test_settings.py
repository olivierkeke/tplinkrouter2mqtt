import os

from tplinkrouter.settings import Settings, ConnectionSettings


def test_settings():
    os.unsetenv("LOG_LEVEL")
    settings = Settings(
        mqtt=ConnectionSettings(host="toto", port=1234),
        tplink=ConnectionSettings(host="toto", port=1234)
    )
    assert settings.log_level == "INFO"


def test_settings_from_env():
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["MQTT__HOST"] = "toto"
    os.environ["MQTT__PORT"] = "1234"
    os.environ["TPLINK__HOST"] = "tata"
    os.environ["TPLINK__PORT"] = "2345"
    settings = Settings()
    assert settings.log_level == os.environ["LOG_LEVEL"]
    assert settings.mqtt.host == os.environ["MQTT__HOST"]
    assert settings.mqtt.port == int(os.environ["MQTT__PORT"])
    assert settings.tplink.host == os.environ["TPLINK__HOST"]
    assert settings.tplink.port == int(os.environ["TPLINK__PORT"])
