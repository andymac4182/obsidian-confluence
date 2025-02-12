"""EuroTempl System
Copyright (c) 2024 Pygmalion Records"""

from . import _cpp

class ParameterGraphManager:
    def __init__(self):
        self._graph = None  # Initialize to None first
        self._dependencies = {}
        self._graph = _cpp.ParameterGraphManager()  # Then create the C++ object

    def add_parameter(self, id: str, name: str, type: str, value: float) -> None:
        self._graph.add_parameter(id, name, type, value)

    def add_dependency(self, source: str, target: str, relation_type: str) -> None:
        if source not in self._dependencies:
            self._dependencies[source] = set()
        self._dependencies[source].add((target, relation_type))

    def get_affected_parameters(self, param_id: str) -> list:
        affected = []
        if param_id in self._dependencies:
            for target, _ in self._dependencies[param_id]:
                affected.append(target)
                affected.extend(self.get_affected_parameters(target))
        return list(set(affected))