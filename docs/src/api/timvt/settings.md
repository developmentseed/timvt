# Module timvt.settings

TiMVT config.

TiVTiler uses pydantic.BaseSettings to either get settings from `.env` or environment variables
see: https://pydantic-docs.helpmanual.io/usage/settings/

## Functions

    
### ApiSettings

```python3
def ApiSettings(
    
) -> timvt.settings._ApiSettings
```

    
This function returns a cached instance of the APISettings object.

Caching is used to prevent re-reading the environment every time the API settings are used in an endpoint.
If you want to change an environment variable and reset the cache (e.g., during testing), this can be done
using the `lru_cache` instance method `get_api_settings.cache_clear()`.

From https://github.com/dmontagu/fastapi-utils/blob/af95ff4a8195caaa9edaa3dbd5b6eeb09691d9c7/fastapi_utils/api_settings.py#L60-L69

    
### PostgresSettings

```python3
def PostgresSettings(
    
) -> timvt.settings._PostgresSettings
```

    
This function returns a cached instance of the APISettings object.

Caching is used to prevent re-reading the environment every time the API settings are used in an endpoint.
If you want to change an environment variable and reset the cache (e.g., during testing), this can be done
using the `lru_cache` instance method `get_api_settings.cache_clear()`.

From https://github.com/dmontagu/fastapi-utils/blob/af95ff4a8195caaa9edaa3dbd5b6eeb09691d9c7/fastapi_utils/api_settings.py#L60-L69

    
### TileSettings

```python3
def TileSettings(
    
) -> timvt.settings._TileSettings
```

    
Cache settings.