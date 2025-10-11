# 使用官方基础镜像构建
FROM rz2014/mineru-vllm:2.5.4

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ="Asia/Shanghai"
ENV MINERU_MODEL_SOURCE=local

LABEL vllm_version="v0.10.1.1"
LABEL maintainer="mineru-server"
LABEL description="MinerU Server with Vllm Backend Support"

# Install additional dependencies
RUN apt-get update && apt-get install -y \
    wget \
    apt-transport-https \
    ca-certificates \
    curl \
    tzdata \
    tini \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

WORKDIR /app

# Copy application files
COPY mineru_server /app/mineru_server
COPY requirements.txt /app/

# Install Flask dependencies
RUN pip3 install --ignore-installed -r requirements.txt -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple

# Set MinerU configuration
ENV PDF_CMD=/usr/local/bin/mineru
ENV MINERU_BACKEND=vlm-vllm-engine
ENV PATH="/usr/local/bin:${PATH}"

# Expose port
EXPOSE 8300

ENTRYPOINT ["tini", "-g", "--"]
CMD ["python3", "mineru_server/app.py"]
