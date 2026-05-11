import numpy as np
from scipy.optimize import fsolve
import pandas as pd
from typing import Dict, List

from src.reservoir import Reservoir
from src.well      import Well
from src.pipe      import Pipe
from src.compressor import DCS
from src.state     import NodeState


class FieldSimulator:

    def __init__(self, reservoir: Reservoir, wells: List[Well],
                 shlyf: Pipe, dcs: DCS):
        self.reservoir = reservoir
        self.wells     = wells
        self.shlyf     = shlyf
        self.dcs       = dcs

    def solve(self, P_res: float) -> Dict[str, NodeState]:

        def equations(x):
            q1, q2, q3, P_man = x
            q1    = max(q1, 0.0)
            q2    = max(q2, 0.0)
            q3    = max(q3, 0.0)
            P_man = max(P_man, self.dcs.P_in() + 0.1)

            qs = [q1, q2, q3]
            F  = []
            for i, well in enumerate(self.wells):
                node  = well.pipe.dp(P_man, qs[i])
                P_bhp = P_man + node.dP
                F.append(well.q(P_res, P_bhp) - qs[i])

            q_total    = q1 + q2 + q3 + self.dcs.q_ext
            node_shlyf = self.shlyf.dp(self.dcs.P_in(), q_total)
            F.append(P_man - (self.dcs.P_in() + node_shlyf.dP))
            return F

        x0  = [500.0, 500.0, 500.0, self.dcs.P_in() + 5.0]
        sol = fsolve(equations, x0, xtol=1e-8, maxfev=2000)

        q1, q2, q3, P_man = sol
        q1    = max(0.0, q1)
        q2    = max(0.0, q2)
        q3    = max(0.0, q3)
        P_man = max(P_man, self.dcs.P_in())

        result: Dict[str, NodeState] = {}
        for i, well in enumerate(self.wells):
            q    = [q1, q2, q3][i]
            node = well.pipe.dp(P_man, q)
            result[f"well_{i+1}"] = NodeState(
                name=f"well_{i+1}",
                P_in=P_man + node.dP,
                P_out=P_man,
                dP=node.dP,
                q_std=q,
                q_res=node.q_res,
                v=node.v,
                rho=node.rho
            )

        q_total         = q1 + q2 + q3 + self.dcs.q_ext
        result["shlyf"] = self.shlyf.dp(self.dcs.P_in(), q_total)
        result["dcs"]   = NodeState(
            name="dcs",
            P_in=self.dcs.P_in(),
            P_out=self.dcs.P_line,
            dP=self.dcs.P_line - self.dcs.P_in(),
            q_std=q_total,
            q_res=None, v=None, rho=None
        )
        return result

    def run(self, N_days: int, dt: float = 1.0) -> pd.DataFrame:
        data  = []
        P_res = self.reservoir.resprops.P
        Gp    = 0.0

        print(f"Запуск симуляции на {N_days} суток...")

        for day in range(N_days):
            if day % 30 == 0:
                print(f"День {day:4d} | P_res = {P_res:.2f} атм")

            states  = self.solve(P_res)
            q1      = states["well_1"].q_std
            q2      = states["well_2"].q_std
            q3      = states["well_3"].q_std
            q_total = q1 + q2 + q3
            P_man   = states["well_1"].P_out

            Gp += q_total * dt
            data.append({
                "t":       day,
                "P_res":   round(P_res, 4),
                "P_man":   round(P_man, 4),
                "q1":      round(q1, 2),
                "q2":      round(q2, 2),
                "q3":      round(q3, 2),
                "q_total": round(q_total, 2),
                "Gp":      round(Gp / 1000.0, 3)
            })

            P_res = self.reservoir.p2(q_total, dt)
            self.reservoir.resprops.P = P_res

        print(f"День {N_days:4d} | P_res = {P_res:.2f} атм")
        print("Симуляция завершена.\n")
        return pd.DataFrame(data)       
