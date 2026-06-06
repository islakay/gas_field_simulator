import math
from src.fluid import Fluid
from src.pipe  import Pipe


class Well:

    def __init__(self, fluid: Fluid, k: float, h: float,
                 re: float, rw: float, pipe: Pipe = None, name: str = "well"):
        self.name   = name
        self.fluid  = fluid
        self.k      = k
        self.h      = h
        self.re     = re
        self.rw     = rw
        self.pipe   = pipe
        self._beta  = 0.00852702
        self._ln    = math.log(re / rw)

    def q(self, P_res: float, P_bhp: float) -> float:
        """
        Дебит скважины по закону Дарси(IPR)

        q = C * (P_res - P_bhp)
        """
        if P_bhp >= P_res or P_res <= 0:
            return 0.0 
        mu    = self.fluid.mu(P_res)
        C     = (self._beta * self.k * self.h) / (mu * self._ln)
        return C * (P_res - P_bhp) / self.fluid.bg (P_res)   

    def ipr(self, P_res: float, n_points: int = 50):
        pts = []
        for i in range(n_points + 1):
            P_bhp = P_res * i / n_points
            pts.append((self.q(P_res, P_bhp), P_bhp))
        return pts

    def vlp(self, P_man: float, q_max: float = 3000.0, n_points: int = 50):
        if self.pipe is None:
            return []
        pts = []
        for i in range(n_points + 1):
            q_val = q_max * i / n_points
            node  = self.pipe.dp(P_man, q_val)
            pts.append((q_val, P_man + node.dP))
        return pts 

    def __str__(self):
        return f"{self.name}(k={self.k}, h={self.h})"       
