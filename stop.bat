@echo off
chcp 65001
echo ============================================
echo          🏢 城市建筑检测系统停止脚本
echo ============================================
echo.

echo ⏹️ 正在停止服务...
docker-compose down

echo.
echo ✅ 服务已停止！
echo.
pause