"""EuroTempl System
Copyright (c) 2024 Pygmalion Records"""

import FreeCAD as App
import Part
from django.contrib.gis.geos import GEOSGeometry, Point

def freecad_to_geos(shape):
    """Convert FreeCAD shape to GEOS geometry for PostGIS storage."""
    # Extract vertices from FreeCAD shape
    vertices = []
    for vertex in shape.Vertexes:
        vertices.append(f"({vertex.X} {vertex.Y} {vertex.Z})")
    
    # Create GEOS geometry (MultiPoint for now, can be extended for other types)
    wkt = f'MULTIPOINT Z ({", ".join(vertices)})'
    geos_geom = GEOSGeometry(wkt)
    return geos_geom

def geos_to_freecad(geos_geom):
    """Convert GEOS geometry to FreeCAD shape."""
    import FreeCAD as App
    
    # Create a new FreeCAD document
    doc = App.newDocument()
    
    if isinstance(geos_geom, Point):
        # For Points, use x, y, z properties directly
        return App.Vector(geos_geom.x, geos_geom.y, geos_geom.z)
    else:
        # For other geometries (LineString, Polygon, etc.)
        points = []
        for coord in geos_geom.coords:
            points.append(App.Vector(coord[0], coord[1], coord[2]))
        return points