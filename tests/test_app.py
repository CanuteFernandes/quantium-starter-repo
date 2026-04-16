from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import app


def _walk(component):
    yield component
    children = getattr(component, "children", None)
    if children is None:
        return
    if isinstance(children, (list, tuple)):
        for child in children:
            if isinstance(child, (str, int, float, bool, type(None), dict)):
                continue
            yield from _walk(child)
    elif not isinstance(children, (str, int, float, bool, type(None), dict)):
        yield from _walk(children)


def test_header_is_present():
    components = list(_walk(app.layout))
    headers = [c for c in components if c.__class__.__name__ == "H1"]
    assert headers, "Expected at least one H1 header in layout"
    assert "Pink Morsel Sales Visualiser" in headers[0].children


def test_visualization_is_present():
    components = list(_walk(app.layout))
    graph_ids = [getattr(c, "id", None) for c in components]
    assert "sales-line-chart" in graph_ids


def test_region_picker_is_present():
    components = list(_walk(app.layout))
    component_ids = [getattr(c, "id", None) for c in components]
    assert "region-filter" in component_ids
