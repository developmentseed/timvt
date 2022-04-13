# Module timvt.factory

timvt.endpoints.factory: router factories.

None

## Variables

```python3
TILE_RESPONSE_PARAMS
```

```python3
templates
```

## Functions

    
### queryparams_to_kwargs

```python3
def queryparams_to_kwargs(
    q: starlette.datastructures.QueryParams,
    ignore_keys: List = []
) -> Dict
```

    
Convert query params to dict.

## Classes

### TMSFactory

```python3
class TMSFactory(
    supported_tms: Type[timvt.dependencies.TileMatrixSetNames] = <enum 'TileMatrixSetNames'>,
    tms_dependency: Callable[..., morecantile.models.TileMatrixSet] = <function TileMatrixSetParams at 0x12454a5e0>,
    router: fastapi.routing.APIRouter = <factory>,
    router_prefix: str = ''
)
```

#### Class variables

```python3
router_prefix
```

```python3
supported_tms
```

#### Methods

    
#### register_routes

```python3
def register_routes(
    self
)
```

    
Register TMS endpoint routes.

    
#### tms_dependency

```python3
def tms_dependency(
    TileMatrixSetId: timvt.dependencies.TileMatrixSetNames = Query(TileMatrixSetNames.WebMercatorQuad)
) -> morecantile.models.TileMatrixSet
```

    
TileMatrixSet parameters.

    
#### url_for

```python3
def url_for(
    self,
    request: starlette.requests.Request,
    name: str,
    **path_params: Any
) -> str
```

    
Return full url (with prefix) for a specific endpoint.

### VectorTilerFactory

```python3
class VectorTilerFactory(
    router: fastapi.routing.APIRouter = <factory>,
    tms_dependency: Callable[..., morecantile.models.TileMatrixSet] = <function TileMatrixSetParams at 0x12454a5e0>,
    layer_dependency: Callable[..., timvt.layer.Layer] = <function LayerParams at 0x12454a820>,
    with_tables_metadata: bool = False,
    with_functions_metadata: bool = False,
    with_viewer: bool = False,
    router_prefix: str = ''
)
```

#### Class variables

```python3
router_prefix
```

```python3
with_functions_metadata
```

```python3
with_tables_metadata
```

```python3
with_viewer
```

#### Methods

    
#### layer_dependency

```python3
def layer_dependency(
    request: starlette.requests.Request,
    layer: str = Path(Ellipsis)
) -> timvt.layer.Layer
```

    
Return Layer Object.

    
#### register_functions_metadata

```python3
def register_functions_metadata(
    self
)
```

    
Register function metadata endpoints.

    
#### register_routes

```python3
def register_routes(
    self
)
```

    
Register Routes.

    
#### register_tables_metadata

```python3
def register_tables_metadata(
    self
)
```

    
Register metadata endpoints.

    
#### register_tiles

```python3
def register_tiles(
    self
)
```

    
Register /tiles endpoints.

    
#### register_viewer

```python3
def register_viewer(
    self
)
```

    
Register viewer.

    
#### tms_dependency

```python3
def tms_dependency(
    TileMatrixSetId: timvt.dependencies.TileMatrixSetNames = Query(TileMatrixSetNames.WebMercatorQuad)
) -> morecantile.models.TileMatrixSet
```

    
TileMatrixSet parameters.

    
#### url_for

```python3
def url_for(
    self,
    request: starlette.requests.Request,
    name: str,
    **path_params: Any
) -> str
```

    
Return full url (with prefix) for a specific endpoint.