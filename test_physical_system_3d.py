import unittest
import math
from physical_system import PhysicalSystem

class TestPhysicalSystem3D(unittest.TestCase):
    def setUp(self):
        self.obj_3d = PhysicalSystem("obj1", 1.0, (0, 0, 0))
        self.obj_2d = PhysicalSystem("obj2", 1.0, (0, 0))  # 测试二维兼容性

    def test_3d_initialization(self):
        """测试三维初始化"""
        self.assertEqual(self.obj_3d.position, (0, 0, 0))
        self.assertEqual(self.obj_3d.velocity, (0, 0, 0))
        self.assertEqual(self.obj_3d.acceleration, (0, 0, 0))

    def test_2d_compatibility(self):
        """测试二维兼容性"""
        self.assertEqual(self.obj_2d.position, (0, 0, 0))  # 自动补零
        self.assertEqual(self.obj_2d.velocity, (0, 0, 0))
        self.assertEqual(self.obj_2d.acceleration, (0, 0, 0))

    def test_3d_gravity(self):
        """测试三维重力"""
        # 默认向下重力
        self.obj_3d.add_gravity()
        forces = self.obj_3d.forces
        self.assertEqual(forces[0][0], 'gravity')
        self.assertAlmostEqual(forces[0][2], -9.8, places=5)  # y方向
        
        # 自定义方向重力
        self.obj_3d.forces = []
        self.obj_3d.add_gravity(direction=(1, 0, 0))  # x方向重力
        self.assertAlmostEqual(self.obj_3d.forces[0][1], 9.8, places=5)
        
        # 斜向重力
        self.obj_3d.forces = []
        self.obj_3d.add_gravity(direction=(1, 1, 1))
        force = self.obj_3d.forces[0]
        mag = math.sqrt(force[1]**2 + force[2]**2 + force[3]**2)
        self.assertAlmostEqual(mag, 9.8, places=5)

    def test_3d_external_force(self):
        """测试三维外力"""
        # 三维向量力
        self.obj_3d.add_external_force("push", 10, (1, 0, 0))
        force = self.obj_3d.forces[0]
        self.assertEqual(force, ('push', 10, 1, 0, 0))
        
        # 欧拉角力
        self.obj_3d.forces = []
        self.obj_3d.add_external_force("pull", 10, (45, 45))  # alpha=45°, beta=45°
        force = self.obj_3d.forces[0]
        self.assertAlmostEqual(force[2], 0.5, places=5)  # x分量
        self.assertAlmostEqual(force[3], 0.5, places=5)  # y分量
        self.assertAlmostEqual(force[4], math.sqrt(2)/2, places=5)  # z分量

    def test_3d_kinematics(self):
        """测试三维运动学更新"""
        # 添加z方向力
        self.obj_3d.add_external_force("thrust", 1, (0, 0, 1))
        self.obj_3d.update_kinematics(1.0)  # 1秒时间
        
        # 验证位置和速度
        self.assertAlmostEqual(self.obj_3d.position[2], 0.5)  # z=0.5*a*t²=0.5
        self.assertAlmostEqual(self.obj_3d.velocity[2], 1.0)  # v=a*t=1

    def test_3d_contact_surface(self):
        """测试三维接触面"""
        obj2 = PhysicalSystem("obj2", 1.0, (1, 1, 1))
        # 三维法线向量
        contact = self.obj_3d.add_contact_surface("contact1", obj2, (1, 1, 1))
        normal = contact['normal_direction']
        mag = math.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2)
        self.assertAlmostEqual(mag, 1.0, places=5)  # 归一化验证
        
        # 二维兼容性
        contact = self.obj_3d.add_contact_surface("contact2", obj2, 45)  # 45度角
        normal = contact['normal_direction']
        self.assertAlmostEqual(normal[0], math.sqrt(2)/2, places=5)
        self.assertAlmostEqual(normal[1], math.sqrt(2)/2, places=5)
        self.assertEqual(normal[2], 0)

    def test_zero_mass_3d(self):
        """测试三维零质量处理"""
        zero_mass = PhysicalSystem("zero", 0, (0, 0, 0))
        zero_mass.add_external_force("force", 10, (1, 1, 1))
        with self.assertRaises(ZeroDivisionError):
            zero_mass.calculate_net_force()

if __name__ == '__main__':
    import sys
    unittest.main(argv=sys.argv)
