from datetime import timedelta

DOMAIN = "my_secret_garden"
CONF_API_URL = "api_url"
CONF_API_KEY = "api_key"

MANUFACTURER = "My Secret Garden"
SCAN_INTERVAL = timedelta(minutes=15)

# Device / unique id prefixes kept from v1 so existing installs keep their devices and entities
DEVICE_GLOBAL = "global_garden"
DEVICE_SEEDLINGS = "godets_garden"
LEGACY_PREFIX = {"bed": "bac", "pot": "pot"}
