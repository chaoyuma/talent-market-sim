# 必做

## 环境
### 前端
vue 3
vite
echart
### 后端
python 3.10
venv环境
FastAPI
Mesa
### 数据库
MYSQL


## 数据库结构数据转储
D:\software\workspace\talent-market-sim\数据库转储
talent_market_sim.sql
# 配置
talent-market-sim\backend\.env
```
APP_NAME=Talent Market Simulation System
APP_HOST=127.0.0.1
APP_PORT=8000
APP_DEBUG=true

OUTPUT_DIR=outputs

MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=自己的
MYSQL_DB=talent_market_sim

LLM_API_KEY=自己的key
LLM_BASE_URL=自己的urlhttps://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=自己的qwen-plus
```
# 后端启动
talent-market-sim\backend
在虚拟环境中运行
venv\Scripts\activate
uvicorn app.main:app --reload
# 前端启动
talent-market-sim\frontend
npm run dev
# 其他说明
## 数据生成
talent-market-sim\数据生成脚本
mysql_seed_generator.py用于微观数据生成

