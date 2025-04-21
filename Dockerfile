FROM --platform=linux/amd64 python:3.9-slim

WORKDIR /app

# 安装系统依赖（关键：添加 libpcre3-dev）
RUN apt-get update && \
    apt-get install -y gcc python3-dev libpcre3-dev && \
    rm -rf /var/lib/apt/lists/*

# 安装应用依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt uwsgi==2.0.21

# 复制应用代码并直接设置权限（关键修改点）
COPY --chown=1001:1001 . .

# 创建非root用户（直接使用 UID 1001）
RUN useradd -u 1001 -d /app -s /bin/false appuser

# 指定用户和工作目录
USER 1001
WORKDIR /app

# 修正后的 CMD 指令（HTTP 模式 + 关键参数）
CMD ["uwsgi","--master","--processes=2","--http=0.0.0.0:5050","--module=app:app","--enable-threads","--lazy-apps","--vacuum"]