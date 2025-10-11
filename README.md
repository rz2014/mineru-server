# MINERU-SERVER

MinerU Server 是一个基于 [MinerU](https://github.com/opendatalab/MinerU) 的 PDF 解析服务，支持 vllm 后端加速。

## 环境依赖

- Python 3.10+
- MinerU: <https://github.com/opendatalab/MinerU>
- 推荐 GPU 支持（使用 vllm 后端时）

## 启动服务

```bash
git clone https://github.com/rz2014/mineru-server.git
cd mineru-server
pip3 install --ignore-installed -r requirements.txt -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
python3 mineru_server/app.py
```

服务将在 `http://0.0.0.0:8300` 上启动。

## 环境变量配置

如果需要自定义配置，可以设置以下环境变量：

```bash
# MinerU 命令路径（默认：mineru）
export PDF_CMD=mineru

# MinerU 解析后端（默认：vlm-vllm-engine）
# 可选值：pipeline, vlm-transformers, vlm-vllm-engine, vlm-http-client
export MINERU_BACKEND=vlm-vllm-engine

# 模型源（默认：local）
# 可选值：huggingface, modelscope, local
export MINERU_MODEL_SOURCE=local

# 存储路径（默认：storage）
export STORAGE_LOCAL_PATH=/path/to/storage

# 最大工作线程数（默认：1）
export MAX_WORKER=2

# 最大任务队列大小（默认：1）
export MAX_TASK_SIZE=5
```

## Docker 部署

```bash
docker run -d \
  -p 8300:8300 \
  --name mineru-server \
  rz2014/mineru-server:latest
```

## Helm 部署

```bash
helm install mineru-server charts
```

## 制作镜像

```bash
docker build -f Dockerfile -t mineru-server:latest .
```

## API 使用

### 1. 上传 PDF 文件进行解析（远程模式）

```bash
curl -X POST http://localhost:8300/api/v1/pdf/remote \
  -F "file=@/path/to/your/file.pdf"
```

返回：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "task_id": "uuid-string"
  }
}
```

### 2. 解析本地 PDF 文件（本地模式）

```bash
curl -X POST http://localhost:8300/api/v1/pdf/local \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/file.pdf",
    "output_dir": "/path/to/output",
    "type": "auto"
  }'
```

### 3. 查询任务状态

```bash
curl http://localhost:8300/api/v1/pdf/remote/<task_id>
```

### 4. 下载解析结果

```bash
curl http://localhost:8300/api/v1/pdf/download/<task_id> -o result.tar.gz
```

## 更新说明

本项目已升级支持 MinerU vllm 后端：

### 主要变化

1. **命令名称变更**：`magic-pdf` → `mineru`
2. **新增后端支持**：支持 vlm-vllm-engine 后端加速
3. **Docker 镜像更新**：基于 `mineru-vllm:v1.0` 基础镜像
4. **新增环境变量**：`MINERU_BACKEND`、`MINERU_MODEL_SOURCE`


### 后端选择建议

- **vlm-vllm-engine**（默认）：最快速度，需要 GPU 支持
- **pipeline**：最佳兼容性，支持 CPU/GPU
- **vlm-transformers**：GPU 加速，兼容性较好
- **vlm-http-client**：连接远程 API 服务

## 参考文档

- [MinerU GitHub](https://github.com/opendatalab/MinerU)
- [MinerU 官方文档](https://opendatalab.github.io/MinerU/zh/)
