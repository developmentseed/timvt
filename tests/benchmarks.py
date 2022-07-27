"""Benchmark tile."""

import pytest


@pytest.mark.parametrize("tms", ["WGS1984Quad", "WebMercatorQuad"])
@pytest.mark.parametrize("tile", ["0/0/0", "4/8/5", "6/33/25"])
def test_benchmark_tile(benchmark, tile, tms, app):
    """Benchmark items endpoint."""

    def f(input_tms, input_tile):
        return app.get(f"/tiles/{input_tms}/public.landsat_wrs/{input_tile}")

    benchmark.group = f"table-{tms}"

    response = benchmark(f, tms, tile)
    assert response.status_code == 200


@pytest.mark.parametrize("tms", ["WGS1984Quad", "WebMercatorQuad"])
@pytest.mark.parametrize("tile", ["0/0/0", "4/8/5", "6/33/25"])
def test_benchmark_tile_functions(benchmark, tile, tms, app):
    """Benchmark items endpoint."""

    def f(input_tms, input_tile):
        return app.get(f"/tiles/{input_tms}/squares/{input_tile}")

    benchmark.group = f"function-{tms}"

    response = benchmark(f, tms, tile)
    assert response.status_code == 200
