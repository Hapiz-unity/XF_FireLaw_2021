# 消防水泵维保履职尽责 MVP

## 快速启动

### 后端 (FastAPI)

```bash
cd apps/api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

后端将在 http://localhost:8000 启动

### 前端 (Next.js)

```bash
cd apps/web
npm install
npm run dev
```

前端将在 http://localhost:3000 启动

## 功能说明

### 1. 维保打卡视图
- 扫码或选择点位
- 填写5个字段：泵房/末端/栓/联动/结论
- 自动绑定IoT快照（压力、泵运行状态）
- 提交生成工单编号

### 2. 履职尽责证据链
- 按日期/点位查询工单
- 查看工单详情（字段 + 照片 + IoT快照）
- 生成PDF报告

## 目录结构

- `docs/fields_mvp.csv` - 字段规范（数据源）
- `docs/iot_sample_payload.json` - IoT数据结构（数据源）
- `apps/api/` - FastAPI后端
- `apps/web/` - Next.js前端
- `04_output/demo_report_samples/` - PDF报告输出目录

## 生成示例报告

运行后端后，执行：

```bash
cd apps/api
python generate_sample_reports.py
```

将在 `04_output/demo_report_samples/` 生成2个示例PDF报告。

