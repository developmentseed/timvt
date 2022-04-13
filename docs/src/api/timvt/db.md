# Module timvt.db

timvt.db: database events.

None

## Variables

```python3
pg_settings
```

## Functions

    
### close_db_connection

```python3
def close_db_connection(
    app: fastapi.applications.FastAPI
) -> None
```

    
Close connection.

    
### connect_to_db

```python3
def connect_to_db(
    app: fastapi.applications.FastAPI
) -> None
```

    
Connect.

    
### table_index

```python3
def table_index(
    db_pool: buildpg.asyncpg.BuildPgPool
) -> Sequence
```

    
Fetch Table index.