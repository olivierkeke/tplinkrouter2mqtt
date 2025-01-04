# Gateway between TPlink router (via telnet) and MQTT

## Supported devices

* TD-W9970

## Usage

### Docker compose

```
services:
  tplinkrouter2mqtt:
    image: hollysaiqs/tplinkrouter2mqtt:latest
    environment:
      TPLINK__USERNAME: tplink HTTP admin
      TPLINK__PASSWORD: tplink HTTP password
      TPLINK__HOST: "router_host"
      TPLINK__PORT: 23
      MQTT__HOST: "mosquitto_host"
      MQTT__PORT: 1883c
      # MQTT__USERNAME: mqtt broker user
      # MQTT__PASSWORD: mqtt broker password
      # LOG_LEVEL: INFO # optional (default=INFO)
```
