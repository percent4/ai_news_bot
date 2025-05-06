# 使用Python 3.11作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置时区为北京时间
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 复制项目文件
COPY ./src /app/src

# 设置pip镜像源为国内源，并安装依赖
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r /app/src/requirements.txt

# 设置适当的权限
RUN chown -R appuser:appuser /app

# 切换到非root用户
USER appuser

# 运行定时任务
CMD ["python", "-u", "/app/src/ai_news_sender.py"] 