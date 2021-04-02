from typing import Tuple, List, Callable, Dict

Size = int
Name = str

QRegSpec = Tuple[Name, Size]
QRegsSpec = List[QRegSpec]

Value = int
Computation = Callable[[Value], Value]
ComputationsMap = Dict[Name, Computation]
ValuesMap = Dict[Name, Value]
