FROM python:3.11-slim

WORKDIR /app

# 安装依赖（使用阿里云镜像加速）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

# 复制项目文件
COPY . .

# 拼图生成器端口
EXPOSE 7862

# 启动应用
CMD ["python", "app.py"]
