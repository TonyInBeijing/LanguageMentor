# 使用 Python 3.10 作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
COPY src/ ./src/
COPY prompts/ ./prompts/
COPY config/ ./config/

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置 Python 路径
ENV PYTHONPATH=/app/src

# 设置启动命令
CMD ["python", "src/main.py"]