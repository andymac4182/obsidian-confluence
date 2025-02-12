from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import concurrent.futures
from django.core.exceptions import ValidationError
from ..cpp_extensions import ParameterGraphManager

@dataclass
class ParameterConstraint:
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: Optional[float] = None
    unit: Optional[str] = None

@dataclass
class Parameter:
    id: str
    name: str
    type: str
    value: float
    constraints: ParameterConstraint

class ParameterManager:
    def __init__(self):
        self._graph = ParameterGraphManager()
        self._thread_pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=4,
            thread_name_prefix="param_worker"
        )
        self._parameters: Dict[str, Parameter] = {}
    
    def add_parameter(self, parameter: Parameter) -> None:
        self._validate_parameter(parameter)
        self._graph.add_parameter(
            parameter.id,
            parameter.name,
            parameter.type,
            parameter.value
        )
        self._parameters[parameter.id] = parameter
    
    def _validate_parameter(self, parameter: Parameter) -> None:
        if parameter.constraints.min_value is not None:
            if parameter.value < parameter.constraints.min_value:
                raise ValidationError(
                    f"Value {parameter.value} below minimum {parameter.constraints.min_value}"
                )
        
        if parameter.constraints.max_value is not None:
            if parameter.value > parameter.constraints.max_value:
                raise ValidationError(
                    f"Value {parameter.value} above maximum {parameter.constraints.max_value}"
                )
                
        if parameter.constraints.step is not None:
            if abs(parameter.value % parameter.constraints.step) > 1e-10:
                raise ValidationError(
                    f"Value {parameter.value} must be a multiple of step {parameter.constraints.step}"
                )
    
    def update_parameter(self, param_id: str, new_value: float) -> List[str]:
        if param_id not in self._parameters:
            raise KeyError(f"Parameter {param_id} not found")
            
        parameter = self._parameters[param_id]
        parameter.value = new_value
        self._validate_parameter(parameter)
        
        affected = self._graph.get_affected_parameters(param_id)
        futures = []
        
        for affected_id in affected:
            futures.append(
                self._thread_pool.submit(self._update_dependent, affected_id)
            )
        
        concurrent.futures.wait(futures)
        return affected

    def _update_dependent(self, param_id: str) -> None:
        # Implementation will depend on specific update rules
        pass