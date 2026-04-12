import numpy as np

class LinearInterpolator: 

    def __init__(self, xs, ys):
        self.xs = np.asarray(xs, dtype=float)
        self.ys = np.asarray(ys, dtype=float)

        if len(self.xs) != len(self.ys):
            raise ValueError("Длины xs и ys должны быть одинаковыми")
        
        if len(self.xs) < 2:
            raise ValueError("Для интерполяции нужно минимум 2 точки")
        
        if not np.all(np.diff(self.xs) > 0):
            raise ValueError("xs должен быть отсортирован по возрастанию")

    def predict(self, xp: float) -> float:
        """интерполяция значения в точке xp."""
        
        if xp < self.xs[0] or xp > self.xs[-1]:
            raise ValueError(f"Значение xp={xp} выходит за границы интерполяции "
                             f"[{self.xs[0]:.1f}, {self.xs[-1]:.1f}] атм")
        
        return float(np.interp(xp, self.xs, self.ys))