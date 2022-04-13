# Module timvt.dependencies

TiVTiler.dependencies: endpoint's dependencies.

None

## Functions

    
### LayerParams

```python3
def LayerParams(
    request: starlette.requests.Request,
    layer: str = Path(Ellipsis)
) -> timvt.layer.Layer
```

    
Return Layer Object.

    
### TileMatrixSetParams

```python3
def TileMatrixSetParams(
    TileMatrixSetId: timvt.dependencies.TileMatrixSetNames = Query(TileMatrixSetNames.WebMercatorQuad)
) -> morecantile.models.TileMatrixSet
```

    
TileMatrixSet parameters.

    
### TileParams

```python3
def TileParams(
    z: int = Path(Ellipsis),
    x: int = Path(Ellipsis),
    y: int = Path(Ellipsis)
) -> morecantile.commons.Tile
```

    
Tile parameters.

## Classes

### TileMatrixSetNames

```python3
class TileMatrixSetNames(
    /,
    *args,
    **kwargs
)
```

#### Ancestors (in MRO)

* enum.Enum

#### Class variables

```python3
CanadianNAD83_LCC
```

```python3
EuropeanETRS89_LAEAQuad
```

```python3
LINZAntarticaMapTilegrid
```

```python3
NZTM2000
```

```python3
NZTM2000Quad
```

```python3
UPSAntarcticWGS84Quad
```

```python3
UPSArcticWGS84Quad
```

```python3
UTM31WGS84Quad
```

```python3
WGS1984Quad
```

```python3
WebMercatorQuad
```

```python3
WorldCRS84Quad
```

```python3
WorldMercatorWGS84Quad
```

```python3
name
```

```python3
value
```