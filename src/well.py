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

#Небольшой тест IPR кривой

fluid = Fluid(
    M=0.01604,
    rho_c=0.6798,
    xa=0.008858,
    xy=0.000668,
    T=310
)
well1 = Well(
    fluid=fluid,
    k=50.0,      
    h=25.0,      
    re=500.0,    
    rw=0.1,      
    
)

P_res = 100.0                    # пластовое давление
pbhp_values = np.linspace(100, 20, 81)   # от 100 до 20 атм

q_values = []
for pbhp in pbhp_values:
    q = well1.q(P_res, pbhp)
    q_values.append(q)

print("IPR-кривая (примерно):")
for i in range(0, len(pbhp_values), 10):
    print(f"P_bhp = {pbhp_values[i]:5.1f} атм → q = {q_values[i]:6.1f} ст.м³/сут")
    
plt.figure(figsize=(10, 6))
plt.plot(pbhp_values, q_values, 'b-', linewidth=2, label='IPR кривая')
plt.xlabel('Забойное давление P_bhp, атм')
plt.ylabel('Дебит q, ст.м³/сут')
plt.title('Кривая притока при P_res = 100 атм')
plt.grid(True, alpha=0.3)
plt.legend() 
plt.tight_layout()
plt.show()


