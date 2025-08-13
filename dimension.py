# dimension.py
"""
物理量纲类，用于表示和操作物理量的量纲。
"""

class Dimension:
    """物理量纲类，用于表示和操作物理量的量纲。

    该类实现了国际单位制(SI)中的七个基本量纲：
    - 长度(L)
    - 质量(M)
    - 时间(T)
    - 电流(I)
    - 热力学温度(Θ)
    - 物质的量(N)
    - 发光强度(J)

    支持量纲的加减乘除运算，用于物理量的量纲一致性检查。
    """

    def __init__(self,
                 length: float = 0.0,  # 长度量纲指数 (L)
                 mass: float = 0.0,  # 质量量纲指数 (M)
                 time: float = 0.0,  # 时间量纲指数 (T)
                 current: float = 0.0,  # 电流量纲指数 (I)
                 temperature: float = 0.0,  # 温度量纲指数 (Θ)
                 amount: float = 0.0,  # 物质的量纲指数 (N)
                 luminous_intensity: float = 0.0  # 发光强度量纲指数 (J)
                 ):
        """初始化量纲对象。

        Args:
            length: 长度量纲指数，默认为0
            mass: 质量量纲指数，默认为0
            time: 时间量纲指数，默认为0
            current: 电流量纲指数，默认为0
            temperature: 温度量纲指数，默认为0
            amount: 物质的量纲指数，默认为0
            luminous_intensity: 发光强度量纲指数，默认为0
        """
        self.exponents = {
            'length': length,
            'mass': mass,
            'time': time,
            'current': current,
            'temperature': temperature,
            'amount': amount,
            'luminous_intensity': luminous_intensity
        }

    def __getattr__(self, name):
        """动态获取量纲属性。

        允许通过属性方式访问量纲指数，如dim.length获取长度量纲指数。

        Args:
            name: 要获取的量纲名称

        Returns:
            对应的量纲指数

        Raises:
            AttributeError: 当请求的量纲名称不存在时
        """
        if name in self.exponents:
            return self.exponents[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __eq__(self, other):
        """比较两个量纲是否相等。

        两个量纲相等当且仅当所有量纲指数都相等。

        Args:
            other: 另一个Dimension对象

        Returns:
            bool: 如果所有量纲指数相等返回True，否则返回False
        """
        return all(self.exponents[k] == other.exponents[k] for k in self.exponents)

    def __mul__(self, other):
        """量纲相乘运算。

        物理量相乘时，量纲指数相加。例如：
        length^1 * length^2 = length^3
        length^1 * time^-1 = length^1 time^-1 (速度量纲)

        Args:
            other: 另一个Dimension对象

        Returns:
            Dimension: 新的量纲对象，其指数是两个量纲对应指数之和
        """
        return Dimension(**{
            k: self.exponents[k] + other.exponents[k] for k in self.exponents
        })

    def __truediv__(self, other):
        """量纲相除运算。

        物理量相除时，量纲指数相减。例如：
        length^1 / time^1 = length^1 time^-1 (速度量纲)
        mass^1 length^1 / time^2 = mass^1 length^1 time^-2 (力量纲)

        Args:
            other: 另一个Dimension对象

        Returns:
            Dimension: 新的量纲对象，其指数是两个量纲对应指数之差
        """
        return Dimension(**{
            k: self.exponents[k] - other.exponents[k] for k in self.exponents
        })

    def __repr__(self):
        """生成量纲的字符串表示。

        只显示非零的量纲指数，格式为"Dimension(长度^1, 时间^-1)"等。

        Returns:
            str: 量纲的字符串表示
        """
        parts = [f"{k}^{v}" for k, v in self.exponents.items() if v != 0]
        return f"Dimension({', '.join(parts)})" if parts else "Dimension()"

    def as_dict(self, compact=False):
        """将量纲转换为字典形式。

        Args:
            compact: 是否只包含非零量纲，默认为False

        Returns:
            dict: 量纲的字典表示，键为量纲名称，值为对应指数
        """
        if compact:
            return {k: v for k, v in self.exponents.items() if v != 0}
        return self.exponents.copy()

    @classmethod
    def common_quantities(cls):
        """获取常见物理量的标准量纲。

        返回一个字典，包含常见物理量(如速度、加速度、力等)的标准量纲。

        Returns:
            dict: 键为物理量名称，值为对应的Dimension对象
        """
        return {
            'length': Dimension(length=1),
            'mass': Dimension(mass=1),
            'time': Dimension(time=1),
            'current': Dimension(current=1),
            'temperature': Dimension(temperature=1),
            'amount': Dimension(amount=1),
            'luminous_intensity': Dimension(luminous_intensity=1),
            'velocity': Dimension(length=1, time=-1),
            'acceleration': Dimension(length=1, time=-2),
            'force': Dimension(mass=1, length=1, time=-2),
            'energy': Dimension(mass=1, length=2, time=-2),
            'power': Dimension(mass=1, length=2, time=-3),
            'pressure': Dimension(mass=1, length=-1, time=-2),
            'frequency': Dimension(time=-1),
            'electric_charge': Dimension(current=1, time=1),
            'voltage': Dimension(mass=1, length=2, current=-1, time=-3),
            'resistance': Dimension(mass=1, length=2, current=-2, time=-3),
            'capacitance': Dimension(current=2, length=-2, mass=-1, time=4),
            'inductance': Dimension(mass=1, length=2, current=-2, time=-2),
            'magnetic_flux': Dimension(mass=1, length=2, current=-1, time=-2),
            'magnetic_field': Dimension(mass=1, current=-1, time=-2),
            'luminous_flux': Dimension(luminous_intensity=1),
            'illuminance': Dimension(luminous_intensity=1, length=-2)
        }
