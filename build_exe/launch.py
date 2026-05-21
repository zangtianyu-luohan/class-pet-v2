"""
学生积分管理系统 - 桌面启动器
启动后自动打开浏览器
"""
import os
import sys
import threading
import time
import webbrowser

# PyInstaller 打包时的资源路径修正
def resource_path(relative_path):
    """获取资源文件的绝对路径，支持 PyInstaller 打包"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def main():
    # 设置工作目录为 EXE 所在目录（数据库文件存放位置）
    if getattr(sys, 'frozen', False):
        work_dir = os.path.dirname(sys.executable)
    else:
        work_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(work_dir)

    # 设置环境变量
    os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./student_points.db")
    os.environ.setdefault("SECRET_KEY", "spms-local-secret-key-2026")
    os.environ.setdefault("INIT_ADMIN_USER", "admin")
    os.environ.setdefault("INIT_ADMIN_PASS", "Admin123456")

    port = 8866
    url = f"http://localhost:{port}"

    print("=" * 50)
    print("  学生积分管理系统 v2.0")
    print("=" * 50)
    print(f"  服务地址: {url}")
    print(f"  管理后台: {url}/admin-panel")
    print(f"  数据库:   {os.path.abspath('student_points.db')}")
    print(f"  默认管理员: admin / Admin123456")
    print("=" * 50)
    print("  按 Ctrl+C 停止服务")
    print("=" * 50)

    # 延迟打开浏览器
    def open_browser():
        time.sleep(2)
        webbrowser.open(url)

    threading.Thread(target=open_browser, daemon=True).start()

    # 启动 FastAPI
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
