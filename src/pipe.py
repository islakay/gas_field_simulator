import math
from src.fluid import Fluid
from src.state import NodeState

class Pipe:
    """
    Универсальный класс для расчёта гидравлики труб (НКТ и шлейф).
    """

    def __init__(self, 
                 L: float, 
                 D: float, 
                 roughness: float, 
                 fluid: Fluid, 
                 vertical_depth: float = 0.0,
                 name: str = "pipe"):
        
        self.L = L
        self.D = D
        self.roughness = roughness
        self.fluid = fluid
        self.vertical_depth = vertical_depth
        self.name = name

    def _friction_factor(self,Re: float, eps_D: float) -> float:
        """Расчёт коэффициента трения λ (Колбрук-Уайт)"""
        if Re < 2300:
            return 64.0 / Re

        lambda_old = 0.02
        for _ in range(50):
            inner = (eps_D / 3.7) + (2.51 / (Re * math.sqrt(lambda_old)))
            lambda_new = (-2.0 * math.log10(inner)) ** (-2.0)

            if abs(lambda_new - lambda_old) < 1e-6:
                return lambda_new
            lambda_old = lambda_new

        return lambda_old

    def dp(self, P_in: float, q_std: float) -> NodeState:
        if q_std <= 0:
            return NodeState(name=self.name, P_in=P_in, P_out=P_in, dP=0.0,
                           q_std=0.0, q_res=None, v=None, rho=None)

        P_avg = (P_in + P_out)/2

        rho = self.fluid.ro(P_avg)
        mu = self.fluid.mu(P_avg)
        Bg = self.fluid.bg(P_avg)

        q_res = q_std * Bg
        area = math.pi * (self.D / 2) ** 2
        v = (q_res / 86400.0) / area

        Re = (rho * v * self.D) / (mu / 1000.0)
        eps_D = self.roughness / self.D

        lambda_fr = self._friction_factor(Re, eps_D)

        friction = lambda_fr * (self.L / self.D) * (rho * v**2 / 2)
        hydrostatic = rho * 9.81 * self.vertical_depth

        delta_P_atm = (friction + hydrostatic) / 101325.0
        P_out = P_in - delta_P_atm

        return NodeState(
            name=self.name,
            P_in=P_in,
            P_out=max(P_out, 1.0),
            dP=round(delta_P_atm, 4),
            q_std=q_std,
            q_res=round(q_res, 2),
            v=round(v, 3),
            rho=round(rho, 2)
        )