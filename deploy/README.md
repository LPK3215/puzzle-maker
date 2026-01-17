# 部署指南

## 方式一：Docker 部署（推荐）

### 快速部署

```bash
# 1. 克隆项目
git clone https://github.com/LPK3215/puzzle-maker.git
cd puzzle-maker

# 2. 构建并运行
docker build -t puzzle-maker -f deploy/Dockerfile .
docker run -d -p 7862:7862 --name puzzle-maker --restart unless-stopped puzzle-maker

# 3. 访问
# http://你的服务器IP:7862
```

### 使用 Docker Compose

```bash
cd deploy
docker-compose up -d
```

## 方式二：直接部署

```bash
# 1. 克隆项目
git clone https://github.com/LPK3215/puzzle-maker.git
cd puzzle-maker

# 2. 运行部署脚本
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

## 方式三：手动部署

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动应用
python app.py

# 3. 访问 http://localhost:7862
```

## 端口说明

- **默认端口**: 7862
- **Docker 映射**: 7862:7862
- **防火墙**: 需要开放 7862 端口

## 配置 Nginx 反向代理（可选）

```bash
# 1. 安装 Nginx
sudo apt install nginx

# 2. 复制配置
sudo cp deploy/nginx.conf /etc/nginx/sites-available/puzzle-maker
sudo ln -s /etc/nginx/sites-available/puzzle-maker /etc/nginx/sites-enabled/

# 3. 修改配置中的域名和端口
sudo nano /etc/nginx/sites-available/puzzle-maker

# 4. 重启 Nginx
sudo nginx -t
sudo systemctl restart nginx
```

## 常见问题

### 端口被占用

```bash
# 查看端口占用
sudo lsof -i :7862

# 或使用其他端口
# 修改 app.py 中的 server_port 参数
```

### Docker 容器管理

```bash
# 查看日志
docker logs puzzle-maker

# 停止容器
docker stop puzzle-maker

# 启动容器
docker start puzzle-maker

# 重启容器
docker restart puzzle-maker

# 删除容器
docker rm -f puzzle-maker
```

## 更新部署

```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建
docker stop puzzle-maker
docker rm puzzle-maker
docker build -t puzzle-maker -f deploy/Dockerfile .
docker run -d -p 7862:7862 --name puzzle-maker --restart unless-stopped puzzle-maker
```
