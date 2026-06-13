from src.state import NodeState

class DCS:
    """
    Дожимная компрессорная станция (ДКС).
    Повышает давление газа перед подачей в магистральный газопровод.
    """

    def __init__(self, CR: float = 1.5, P_line: float = 5.0, q_ext: float = 0.0):
        """
        CR - степень сжатия >= 1.0
        q_ext - расход стороннего газа, поступающего в манилофльд [ст.м^3/сут] 
        """
        self.CR = CR
        self.P_line = P_line
        self.q_ext = q_ext

    def P_in(self) -> float:

        if self.CR <= 1.0:
            return self.P_line
        
        return self.P_line / self.CR
    
    def set_compression_ratio(self, new_CR: float):
        """
        Для анализа чувствительности
        """

        if new_CR < 1.0:
            new_CR = 1.0
        self.CR = new_CR

