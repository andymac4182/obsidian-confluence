# backend/geometry/tests/conftest.py
"""Pytest configuration for geometry tests"""

import pytest
import FreeCAD as App
import Part

@pytest.fixture(scope="function")
def freecad_doc():
    doc = App.newDocument("TestDoc")
    yield doc
    App.closeDocument(doc.Name)

@pytest.fixture(scope="session")
def cgal_converter():
    from geometry.core.cpp_extensions import cgal_converter
    return cgal_converter.CGALConverter()

@pytest.fixture(scope="session")
def cgal_parametric():
    from geometry.core.cpp_extensions import cgal_parametric
    return cgal_parametric.ParametricShape()