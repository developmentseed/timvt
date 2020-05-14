

###  Create Db

```
$ docker-compose up -d db
```

### Upload data
```bash
$ ogr2ogr -nlt PROMOTE_TO_MULTI -lco GEOMETRY_NAME=geom -t_srs EPSG:4326 -f PostgreSQL PG:"dbname='db' host='localhost' port='5432' user='postgres' password='mypassword'" "demo/country.geojson"

$ ogrinfo PG:"host=localhost port=5432 user='postgres' password='mypassword' dbname='db'" country  -al -so

INFO: Open of `PG:host=localhost port=5432 user='postgres' password='mypassword' dbname='db''
      using driver `PostgreSQL' successful.

Layer name: country
Geometry: Unknown (any)
Feature Count: 177
...
```
