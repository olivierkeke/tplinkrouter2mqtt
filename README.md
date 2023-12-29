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
      TPLINK_USERNAME: tplink HTTP admin
      TPLINK_PASSWORD: tplink HTTP password
      TPLINK_HOST: "router_host"
      MQTT_HOST: "mosquitto_host"
      MQTT_PORT: 1883
      LOG_LEVEL: INFO # optional (default=INFO)
```
