from dataclasses import dataclass
from state import NodeState 
from fluid import Fluid      

@dataclass
class ResProps:
    """
    Контейнер для свойств пласта.
    """
    P: float      # текущее пластовое давление [атм]
    V: float      # объём пласта [м³]
    T: float      # температура пласта [К]


class Reservoir:
    """
    Модель пласта. Отвечает только за материальный баланс.
    Не хранит параметры скважин (k, h, re, rw) — они в Well.
    """

    def __init__(self, resprops: ResProps, fluid: Fluid):
        self.resprops = resprops   # текущее состояние пласта
        self.fluid = fluid         

    def p2(self, q_total: float, dt: float = 1.0) -> float:
       
        if q_total <= 0:
            return self.resprops.P  # ничего не добываем — давление не меняется

        P = self.resprops.P
        V = self.resprops.V
        T = self.resprops.T

        # Плотность газа при текущем пластовом давлении
        rho_res = self.fluid.ro(P)          # кг/м³

        # Плотность при стандартных условиях
        rho_std = self.fluid.ro(1.0)        # примерно при 1 атм

        delta_P = self.fluid.z(P) * (rho_std / rho_res) * (q_total * dt) / V

        P_new = P - delta_P

        return max(P_new, 1.0)
    