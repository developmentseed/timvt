# Create Sentinel/Landsat Grids

### Landsat-8
```
$ wget http://storage.googleapis.com/gcp-public-data-landsat/index.csv.gz
$ cat index.csv.gz | gunzip | grep "LANDSAT_8"  | cut -d',' -f2 | cut -d'_' -f3 | sort | uniq | tail -n +2 > pathrow.txt

$ wget https://prd-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/atoms/files/WRS2_descending_0.zip
$ fio cat WRS2_descending.shp | jq -c '.properties={"PR": .properties.PR, "PATH": .properties.PATH, "ROW": .properties.ROW}' > WRS2_descending.geojson
$ cat WRS2_descending.geojson | python filter.py --tiles pathrow.txt --property PR > landsat_wrs.geojson
$ ogr2ogr -f PGDump landsat_wrs.sql landsat_wrs.geojson -lco GEOMETRY_NAME=geom 
```


### Sentinel-2
```
$ wget https://storage.googleapis.com/gcp-public-data-sentinel-2/index.csv.gz
$ cat index.csv.gz | gunzip | cut -d',' -f1 | cut -d'_' -f10  | sed 's/^T//' | sort | uniq > tiles.txt

$ wget https://sentinel.esa.int/documents/247904/1955685/S2A_OPER_GIP_TILPAR_MPC__20151209T095117_V20150622T000000_21000101T000000_B00.kml
$ ogr2ogr -f "GeoJSON" -t_srs EPSG:4326 S2A_OPER_GIP_TILPAR_MPC__20151209T095117_V20150622T000000_21000101T000000_B00.geojson S2A_OPER_GIP_TILPAR_MPC__20151209T095117_V20150622T000000_21000101T000000_B00.kml
$ cat S2A_OPER_GIP_TILPAR_MPC__20151209T095117_V20150622T000000_21000101T000000_B00.geojson | jq -c '.features[] | .properties={"Name": .properties.Name} | .geometry=(.geometry.geometries | map(select(.type == "Polygon"))[0])' | fio collect  > sentinel2_tiles.geojson

$ fio cat sentinel2_tiles.geojson | python filter.py --tiles tiles.txt --property Name > sentinel_mgrs.geojson
$ ogr2ogr -f PGDump sentinel_mgrs.sql sentinel_mgrs.geojson -lco GEOMETRY_NAME=geom 
```

`filter.py`

```python
# requirements `click cligj fiona`

import json
import click
import cligj


@click.command()
@cligj.features_in_arg
@click.option('--tiles', type=click.Path(exists=True), required=True)
@click.option("--property", type=str, help="Define accessor property", required=True)
def main(features, tiles, property):
    with open(tiles, 'r') as f:
        list_tile = set(f.read().splitlines())

    for feat in features:
        if feat['properties'][property] in list_tile:
            click.echo(json.dumps(feat))


if __name__ == '__main__':
    main()
```