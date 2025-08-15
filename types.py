from dataclasses import dataclass

@dataclass(frozen=True)
class FlowConditions:
    Re: float = 1e6
    Mach: float = 0.8
    Alpha: float = 5.0