import unittest
import sys
from dimension import Dimension


class TestDimension(unittest.TestCase):

    def test_initialization(self):
        # 测试默认初始化
        dim_default = Dimension()
        self.assertEqual(dim_default.length, 0.0)
        self.assertEqual(dim_default.mass, 0.0)

        # 测试带参数初始化
        dim_custom = Dimension(length=2, mass=1.5, time=-3)
        self.assertEqual(dim_custom.length, 2)
        self.assertEqual(dim_custom.mass, 1.5)
        self.assertEqual(dim_custom.time, -3)

    def test_attribute_access(self):
        dim = Dimension(length=1, temperature=-2)
        # 测试存在属性
        self.assertEqual(dim.length, 1)
        self.assertEqual(dim.temperature, -2)

        # 测试不存在属性
        with self.assertRaises(AttributeError):
            self.assertEqual(dim.invalid_attribute, 1)

    def test_equality(self):
        # 完全相等
        dim1 = Dimension(length=1, mass=2)
        dim2 = Dimension(length=1, mass=2)
        self.assertEqual(dim1, dim2)

        # 部分不相等
        dim3 = Dimension(length=1, mass=1)
        self.assertNotEqual(dim1, dim3)

        # 所有属性都为零
        dim_zero1 = Dimension()
        dim_zero2 = Dimension()
        self.assertEqual(dim_zero1, dim_zero2)

    def test_multiplication(self):
        dim1 = Dimension(length=2, mass=1)
        dim2 = Dimension(length=-1, time=3)

        # 测试乘法
        result = dim1 * dim2
        self.assertEqual(result.length, 1)
        self.assertEqual(result.mass, 1)
        self.assertEqual(result.time, 3)

        # 测试标量单位
        scalar = Dimension()
        self.assertEqual(dim1 * scalar, dim1)

    def test_division(self):
        dim1 = Dimension(length=3, time=2)
        dim2 = Dimension(length=1, time=1)

        # 测试除法
        result = dim1 / dim2
        self.assertEqual(result.length, 2)
        self.assertEqual(result.time, 1)

        # 测试自除
        self.assertEqual(dim1 / dim1, Dimension())

    def test_repr(self):
        # 测试标准表示
        dim_full = Dimension(length=1, mass=-2, time=0)
        self.assertEqual(repr(dim_full), "Dimension(length^1, mass^-2)")

        # 测试零量纲表示
        self.assertEqual(repr(Dimension()), "Dimension()")

    def test_as_dict(self):
        # 测试完整字典
        dim = Dimension(current=1.5, amount=-3)
        full_dict = dim.as_dict()
        self.assertEqual(full_dict, {
            'length': 0.0, 'mass': 0.0, 'time': 0.0,
            'current': 1.5, 'temperature': 0.0,
            'amount': -3, 'luminous_intensity': 0.0
        })

        # 测试紧凑字典
        compact_dict = dim.as_dict(compact=True)
        self.assertEqual(compact_dict, {'current': 1.5, 'amount': -3})

    def test_common_quantities(self):
        # 测试常见物理量
        quantities = Dimension.common_quantities()

        # 检查部分常用物理量
        self.assertEqual(quantities['length'], Dimension(length=1))
        self.assertEqual(quantities['velocity'], Dimension(length=1, time=-1))
        self.assertEqual(quantities['force'], Dimension(mass=1, length=1, time=-2))
        self.assertEqual(quantities['voltage'],
                         Dimension(mass=1, length=2, current=-1, time=-3))


if __name__ == '__main__':
    runner = unittest.TextTestRunner(stream=sys.stdout)
    unittest.main(testRunner=runner)
