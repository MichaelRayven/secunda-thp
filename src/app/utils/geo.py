from typing import Any

from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape
from shapely.geometry.base import BaseGeometry


def wkb_to_shape(wkb: WKBElement | BaseGeometry) -> BaseGeometry | None:
    if isinstance(wkb, WKBElement):
        return to_shape(wkb)

    return wkb


def dump_geom(value: Any):
    if isinstance(value, dict):
        return value
    return getattr(wkb_to_shape(value), '__geo_interface__', None)
