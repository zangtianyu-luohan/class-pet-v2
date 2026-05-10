@echo off
echo ========================================
echo  学生积分管理系统 - 文档重新生成
echo ========================================
cd /d "%~dp0"
echo.
echo [1/3] 生成开发手册...
node gen_dev_manual.js
echo [2/3] 生成运维手册...
node gen_ops_manual.js
echo [3/3] 生成用户使用手册...
node gen_user_manual.js
echo.
echo ========================================
echo  全部完成！文档已输出到 ../ 目录
echo ========================================
pause
