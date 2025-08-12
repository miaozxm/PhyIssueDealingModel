
from physical_system import PhysicalSystem, Vector
import math
# ================ 测试用例 ================
import unittest
import sys


class TestPhysicalSystemVectorized(unittest.TestCase):
    def setUp(self):
        self.obj_3d = PhysicalSystem("obj1", 1.0, (0, 0, 0))
        self.obj_2d = PhysicalSystem("obj2", 1.0, (0, 0))  # 测试二维兼容性
        print("测试用例初始化完成")

    def test_vector_class(self):
        """测试Vector类基本操作"""
        v1 = Vector(1, 2, 3)
        v2 = Vector(3, 2, 1)
        print("v1", type(v1))

        # 加法
        self.assertEqual((v1 + v2).as_tuple(), (4, 4, 4))

        # 标量乘法
        self.assertEqual((v1 * 2).as_tuple(), (2, 4, 6))

        # 归一化
        v = Vector(3, 0, 0)
        self.assertEqual(v.normalized().as_tuple(), (1, 0, 0))

        # 点积
        self.assertEqual(v1.dot(v2), 10)

        # 叉积
        self.assertEqual(v1.cross(v2).as_tuple(), (-4, 8, -4))

        print("Vector类测试通过")

    def test_3d_gravity(self):
        """测试三维重力"""
        # 默认向下重力
        gravity = self.obj_3d.add_gravity()
        self.assertEqual(gravity.as_tuple(), (0, -9.8, 0))
        print("gravity", type(gravity))
        # 自定义方向重力
        gravity = self.obj_3d.add_gravity(direction=(1, 0, 0))
        self.assertAlmostEqual(gravity.as_tuple()[0], 9.8, places=5)

        # 斜向重力
        gravity = self.obj_3d.add_gravity(direction=(1, 1, 1))
        mag = math.sqrt(gravity.as_tuple()[0] ** 2 +
                        gravity.as_tuple()[1] ** 2 +
                        gravity.as_tuple()[2] ** 2)
        self.assertAlmostEqual(mag, 9.8, places=5)
        print("三维重力测试通过")

    def test_3d_external_force(self):
        """测试三维外力"""
        # 三维向量力
        force = self.obj_3d.add_external_force("push", 10, (1, 0, 0))
        self.assertEqual(force.as_tuple(), (10, 0, 0))
        print("force", type(force))

        # 欧拉角力
        force = self.obj_3d.add_external_force("pull", 10, (45, 45))
        self.assertAlmostEqual(force.as_tuple()[0], 10 * 0.5, places=5)
        self.assertAlmostEqual(force.as_tuple()[1], 10 * 0.5, places=5)
        self.assertAlmostEqual(force.as_tuple()[2], 10 * math.sqrt(2) / 2, places=5)

        # Vector对象输入
        force = self.obj_3d.add_external_force("vector", 10, Vector(0, 1, 0))
        self.assertEqual(force.as_tuple(), (0, 10, 0))
        print("三维外力测试通过")

    def test_3d_kinematics(self):
        """测试三维运动学更新（关键修复）"""
        # 添加z方向力
        self.obj_3d.add_external_force("thrust", 1, (0, 0, 1))
        self.obj_3d.update_kinematics(1.0)  # 1秒时间

        # 验证位置和速度
        self.assertAlmostEqual(self.obj_3d.position.as_tuple()[2], 0.5)  # z=0.5*a*t²=0.5
        self.assertAlmostEqual(self.obj_3d.velocity.as_tuple()[2], 1.0)  # v=a*t=1
        print("三维运动学更新测试通过")

    def test_contact_surface(self):
        """测试接触面"""
        obj2 = PhysicalSystem("obj2", 1.0, (1, 1, 1))
        # 三维法线向量
        contact = self.obj_3d.add_contact_surface("contact1", obj2, (1, 1, 1))
        normal = contact['normal_direction']
        self.assertAlmostEqual(normal.magnitude(), 1.0, places=5)  # 归一化验证

        # Vector对象输入
        contact = self.obj_3d.add_contact_surface("contact2", obj2, Vector(0, 1, 0))
        self.assertEqual(contact['normal_direction'].as_tuple(), (0, 1, 0))
        print("接触面测试通过")

    def test_serialization(self):
        """测试序列化"""
        obj = PhysicalSystem("test", 1.0, (1, 2, 3))
        obj.add_gravity()
        obj.add_external_force("test_force", 10, (45, 0))

        data = obj.to_dict()
        self.assertEqual(data['position'], (1.0, 2.0, 3.0))
        self.assertEqual(len(data['forces']), 2)
        print("序列化测试通过")


if __name__ == '__main__':
    runner = unittest.TextTestRunner(stream=sys.stdout)
    unittest.main(testRunner=runner)
