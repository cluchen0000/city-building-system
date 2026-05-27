@echo off
chcp 65001
echo ============================================
echo          🏢 城市建筑检测系统启动脚本
echo ============================================
echo.

echo 📦 正在启动服务...
docker-compose up -d

echo.
echo ✅ 服务启动完成！
echo.
echo 📍 访问地址：
echo    前端页面: http://localhost
echo    后端API:  http://localhost:8000
echo    API文档:  http://localhost:8000/docs
echo.
echo 📋 常用命令：
echo    停止服务: docker-compose down
echo    查看日志: docker-compose logs -f
echo    重启服务: docker-compose restart
echo.
pause