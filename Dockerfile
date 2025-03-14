FROM rz2014/magic-pdf:latest

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ="Asia/Shanghai"

LABEL ubuntu.version="22.04"
LABEL tini.version="0.18.0"

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

COPY mineru_server /app/mineru_server
COPY requirements.txt /app/
RUN /bin/bash -c "source /opt/mineru_venv/bin/activate && \
    pip3 install -r requirements.txt -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple"

ENV PDF_CMD=/opt/mineru_venv/bin/magic-pdf
ENV PATH="/opt/mineru_venv/bin:${PATH}"

ENTRYPOINT ["tini", "-g", "--"]
CMD ["python3", "mineru_server/app.py"]