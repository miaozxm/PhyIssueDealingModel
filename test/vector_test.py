import unittest
import sys
from vector import *


class TestVector(unittest.TestCase):
    def test_vector_initialization(self):
        # 测试默认量纲初始化
        v1 = Vector(1.0, 2.0, 3.0)
        self.assertEqual(v1.x, 1.0)
        self.assertEqual(v1.y, 2.0)
        self.assertEqual(v1.z, 3.0)
        self.assertEqual(v1.dimension, Dimension())

        # 测试自定义量纲初始化
        dim = Dimension(length=1, time=-1)
        v2 = Vector(4.0, 5.0, 6.0, dimension=dim)
        self.assertEqual(v2.x, 4.0)
        self.assertEqual(v2.y, 5.0)
        self.assertEqual(v2.z, 6.0)
        self.assertEqual(v2.dimension, dim)

    def test_addition(self):
        # 同量纲矢量加法
        v1 = Vector(1, 2, 3, Dimension(length=1))
        v2 = Vector(4, 5, 6, Dimension(length=1))
        result = v1 + v2
        self.assertEqual(result.x, 5)
        self.assertEqual(result.y, 7)
        self.assertEqual(result.z, 9)
        self.assertEqual(result.dimension, Dimension(length=1))

        # 不同量纲矢量加法应报错
        v3 = Vector(1, 2, 3, Dimension(mass=1))
        with self.assertRaises(ValueError) as cm:
            v1 + v3
        self.assertIn("矢量量纲不匹配", str(cm.exception))

    def test_subtraction(self):
        # 同量纲矢量减法
        v1 = Vector(5, 10, 15, Dimension(time=1))
        v2 = Vector(1, 2, 3, Dimension(time=1))
        result = v1 - v2
        self.assertEqual(result.x, 4)
        self.assertEqual(result.y, 8)
        self.assertEqual(result.z, 12)
        self.assertEqual(result.dimension, Dimension(time=1))

        # 不同量纲矢量减法应报错
        v3 = Vector(1, 2, 3, Dimension(time=-1))
        with self.assertRaises(ValueError) as cm:
            v1 - v3
        self.assertIn("矢量量纲不匹配", str(cm.exception))

    def test_scalar_multiplication(self):
        # 右乘标量
        v = Vector(1, 2, 3, Dimension(mass=1))
        result_right = v * 3
        self.assertEqual(result_right.x, 3)
        self.assertEqual(result_right.y, 6)
        self.assertEqual(result_right.z, 9)
        self.assertEqual(result_right.dimension, Dimension(mass=1))

        # 左乘标量
        result_left = 4 * v
        self.assertEqual(result_left.x, 4)
        self.assertEqual(result_left.y, 8)
        self.assertEqual(result_left.z, 12)
        self.assertEqual(result_left.dimension, Dimension(mass=1))

        # 非数值乘法应报错
        with self.assertRaises(TypeError) as cm:
            v * "string"
        self.assertIn("必须是数值类型", str(cm.exception))

    def test_magnitude(self):
        # 测试模长计算
        v = Vector(3, 4, 0)
        self.assertEqual(v.magnitude(), 5.0)

        v = Vector(1, 1, 1)
        self.assertAlmostEqual(v.magnitude(), math.sqrt(3))

        v = Vector(0, 0, 0)
        self.assertEqual(v.magnitude(), 0.0)

    def test_normalized(self):
        # 测试归一化
        v = Vector(3, 4, 0)
        normalized_v = v.normalized()
        self.assertEqual(normalized_v.x, 0.6)
        self.assertEqual(normalized_v.y, 0.8)
        self.assertEqual(normalized_v.z, 0.0)
        self.assertEqual(normalized_v.magnitude(), 1.0)
        self.assertEqual(normalized_v.dimension, Dimension())

        # 零矢量归一化
        zero_v = Vector(0, 0, 0)
        normalized_zero = zero_v.normalized()
        self.assertEqual(normalized_zero.x, 0.0)
        self.assertEqual(normalized_zero.y, 0.0)
        self.assertEqual(normalized_zero.z, 0.0)
        self.assertEqual(normalized_zero.magnitude(), 0.0)
        self.assertEqual(normalized_zero.dimension, Dimension())

    def test_dot_product(self):
        # 测试点积
        v1 = Vector(1, 2, 3)
        v2 = Vector(4, 5, 6)
        dot_product = v1.dot(v2)
        self.assertEqual(dot_product, 32)

        # 不同量纲应报错
        v3 = Vector(4, 5, 6, Dimension(mass=1))
        with self.assertRaises(ValueError) as cm:
            v1.dot(v3)
        self.assertIn("矢量量纲不匹配", str(cm.exception))

    def test_cross_product(self):
        # 测试叉积
        v1 = Vector(1, 0, 0)
        v2 = Vector(0, 1, 0)
        cross_product = v1.cross(v2)
        self.assertEqual(cross_product.x, 0)
        self.assertEqual(cross_product.y, 0)
        self.assertEqual(cross_product.z, 1)

        # 测试叉积量纲（应相加）
        dim1 = Dimension(mass=1)
        dim2 = Dimension(length=1)
        v3 = Vector(1, 2, 3, dim1)
        v4 = Vector(4, 5, 6, dim2)
        result = v3.cross(v4)
        expected_dim = Dimension(mass=1, length=1)
        self.assertEqual(result.dimension, expected_dim)

    def test_subclasses(self):
        # 测试位移类
        d = Displacement(3, 4, 5)
        self.assertEqual(d.x, 3.0)
        self.assertEqual(d.y, 4.0)
        self.assertEqual(d.z, 5.0)
        self.assertEqual(d.dimension, Dimension(length=1))

        # 测试速度类
        v = Velocity(10, 0, -5)
        self.assertEqual(v.x, 10.0)
        self.assertEqual(v.y, 0.0)
        self.assertEqual(v.z, -5.0)
        self.assertEqual(v.dimension, Dimension(length=1, time=-1))

        # 测试力类
        f = Force(0, 9.8, 0)
        self.assertEqual(f.x, 0.0)
        self.assertEqual(f.y, 9.8)
        self.assertEqual(f.z, 0.0)
        self.assertEqual(f.dimension, Dimension(mass=1, length=1, time=-2))

        # 测试加速度类
        a = Acceleration(0, -9.8, 0)
        self.assertEqual(a.x, 0.0)
        self.assertEqual(a.y, -9.8)
        self.assertEqual(a.z, 0.0)
        self.assertEqual(a.dimension, Dimension(length=1, time=-2))


if __name__ == "__main__":
    runner = unittest.TextTestRunner(stream=sys.stdout)
    unittest.main(testRunner=runner)
