# MINERU-SERVER

## 环境依赖

- python 3.10
- mineru: <https://github.com/opendatalab/MinerU?tab=readme-ov-file#quick-cpu-demo>

## 启动

```bash
git clone https://github.com/rz2014/mineru-server.git
cd mineru-server/mineru_server
python3 app.py
```

如果`magic-pdf`不在默认的`PATH`上，需要修改环境变量`PDF_CMD`来手工指定。例如:

```bash
export PDF_CMD=/root/anaconda3/envs/MinerU/bin/magic-pdf
```

## 制作镜像

```bash
docker build -f Dockerfile -t mineru-server:latest .
```

## Helm部署

```bash
helm install mineru-server charts
```
