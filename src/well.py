import math 
import numpy as np
from fluid import Fluid 
from state import NodeState 
import matplotlib.pyplot as plt

class Well:

    def __init__(self,
                 fluid: Fluid,
                 k: float,
                 h: float,
                 re: float,
                 rw: float,
                 ):
    
        self.fluid = fluid 
        self.k = k
        self.h = h 
        self.re = re 
        self.rw = rw
        
        #Формула: C = β * k * h / (μ * ln(re/rw) = ст.м^3/(сут * атм)
        #β = 0.00852702

        beta = 0.00852702
        mu = self.fluid.mu(80)

        self.C = (beta * k * h) / (mu * math.log(re/rw))

    def q(self, P_res: float, P_bhp: float) -> float:
        """
        Дебит скважины по закону Дарси(IPR)

        q = C * (P_res - P_bhp)
        """
        if P_bhp >= P_res:
            return 0.0
        
        return self.C * (P_res - P_bhp)
    
    def calculate_bhp(self, P_man: float, q_std: float) -> float:
        """
        Расчёт забойного давления через НКТ (VLP).
        """
        if self.pipe is None:
            return P_man  # если нет трубы 
        
        node = self.pipe.dp(P_man, q_std)
        return node.P_out

    def get_C(self) -> float:
        """Возвращает коэффициент продуктивности"""
        return self.C