FROM python:3.12-slim

# 安裝系統依賴（PostgreSQL、Redis client 等）
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# 安裝 uv
RUN pip install uv

# 設定工作目錄
WORKDIR /app

# 複製 pyproject.toml 與 uv.lock（若有）
COPY pyproject.toml uv.lock* ./

# 安裝依賴（uv 會自動解析並安裝）
RUN uv pip install --system --no-deps -r <(uv pip compile pyproject.toml)

# 複製整個專案
COPY . .

# 預設啟動指令（可由 docker-compose 覆蓋）
CMD ["uvicorn", "dashboard.main:app", "--host", "0.0.0.0", "--port", "8000"]
