import unittest
import math
from test import PhysicalSystem

class TestPhysicalSystem(unittest.TestCase):
    def setUp(self):
        """测试前初始化一个物理系统"""
        self.system = PhysicalSystem("test_obj", 2.0, (0, 0))

    def test_initialization(self):
        """测试初始化是否正确"""
        self.assertEqual(self.system.id, "test_obj")
        self.assertEqual(self.system.mass, 2.0)
        self.assertEqual(self.system.position, (0, 0))
        self.assertEqual(self.system.velocity, (0, 0))
        self.assertEqual(self.system.acceleration, (0, 0))
        self.assertEqual(len(self.system.forces), 0)
        self.assertEqual(len(self.system.contact_surfaces), 0)
        print("初始化测试通过")

    def test_add_gravity(self):
        """测试添加重力"""
        gravity = self.system.add_gravity()
        self.assertEqual(gravity[0], "gravity")
        self.assertAlmostEqual(gravity[1], -2.0 * 9.8)
        self.assertEqual(len(self.system.forces), 1)
        print("重力添加测试通过")

    def test_add_external_force(self):
        """测试添加外部力"""
        force = self.system.add_external_force("pull", 10, 30)
        self.assertEqual(force[0], "pull")
        self.assertEqual(force[1], 10)
        self.assertEqual(force[2], 30)
        self.assertEqual(len(self.system.forces), 1)
        print("外部力添加测试通过")

    def test_calculate_net_force_single_force(self):
        """测试单个力的合力计算"""
        self.system.add_external_force("pull", 10, 0)  # 水平向右的力
        fx, fy = self.system.calculate_net_force()
        self.assertAlmostEqual(fx, 10)
        self.assertAlmostEqual(fy, 0)
        print("单个力的合力计算测试通过")

    def test_calculate_net_force_multiple_forces(self):
        """测试多个力的合力计算"""
        self.system.add_external_force("pull", 10, 0)  # 水平向右
        self.system.add_external_force("push", 5, 180)  # 水平向左
        self.system.add_gravity()  # 向下
        fx, fy = self.system.calculate_net_force()
        self.assertAlmostEqual(fx, 5)  # 10 - 5 = 5
        self.assertAlmostEqual(fy, -19.6, places=4)  # 允许4位小数精度
        print("多个力的合力计算测试通过")

    def test_update_kinematics(self):
        """测试运动状态更新"""
        self.system.add_external_force("pull", 10, 0)  # 水平向右的力
        self.system.update_kinematics(0.1)  # 时间间隔0.1秒

        # 验证加速度
        ax, ay = self.system.acceleration
        self.assertAlmostEqual(ax, 5)  # F=ma => a=F/m=10/2=5
        self.assertAlmostEqual(ay, 0)

        # 验证速度
        vx, vy = self.system.velocity
        self.assertAlmostEqual(vx, 0.5)  # v=at=5*0.1=0.5
        self.assertAlmostEqual(vy, 0)

        # 验证位置
        px, py = self.system.position
        self.assertAlmostEqual(px, 0.025)  # x=0.5*a*t²=0.5*5*0.01=0.025
        self.assertAlmostEqual(py, 0)
        print("运动状态更新测试通过")

    def test_zero_mass(self):
        """测试零质量情况"""
        zero_mass_system = PhysicalSystem("zero_mass", 0, (0, 0))
        zero_mass_system.add_external_force("pull", 10, 0)
        with self.assertRaises(ZeroDivisionError):
            zero_mass_system.update_kinematics(0.1)
        print("零质量异常处理测试通过")

if __name__ == "__main__":
    unittest.main(verbosity=2)
