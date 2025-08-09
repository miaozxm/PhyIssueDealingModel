import sys
import os
import unittest

def main():
    try:
        # 确保当前目录在Python路径中
        sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

        # 打印当前工作目录和Python路径
        print(f"Current working directory: {os.getcwd()}")
        print(f"Python path: {sys.path}")

        # 加载测试模块
        loader = unittest.TestLoader()
        suite = loader.discover(start_dir=os.path.dirname(__file__), pattern='test_*.py')

        # 运行测试
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        # 返回适当的退出码
        sys.exit(not result.wasSuccessful())

    except Exception as e:
        print(f"Error running tests: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
