# 秋招爬虫框架

一个可扩展的 Scrapy 爬虫，用于每日抓取秋招信息，按大/中/小厂分类入库（SQLite）。

## 功能
- 统一数据结构：公司、网址、职位、岗位要求、招聘要求、发布时间、截止时间、学历要求
- 去重入库：SQLite（`data/jobs.db`）+ 唯一索引
- 公司规模分类：`config/companies.yml`
- 示例爬虫：腾讯（调用公开 API），可扩展其它站点
- 定时任务：`run_all.py`（基于 APScheduler）

## 快速开始
1. 安装依赖
```
pip install -r requirements.txt
```

2. 列出爬虫
```
cd autumn_jobs_crawler
scrapy list
```

3. 运行示例爬虫（输出到 JSON 以便快速查看）
```
cd autumn_jobs_crawler
scrapy crawl tencent -O ../sample.json -s LOG_LEVEL=INFO
```

4. 每日定时运行（开发环境直接跑脚本；线上建议用 cron/systemd）
```
cd autumn_jobs_crawler
python run_all.py
```

## 目录结构
```
autumn_jobs_crawler/
  scrapy.cfg
  run_all.py
  config/
    companies.yml
  data/
    jobs.db (首次运行自动创建)
  autumn_jobs/
    settings.py
    items.py
    db.py
    pipelines.py
    utils.py
    spiders/
      tencent.py
```

## 扩展新站点
- 在 `autumn_jobs/spiders/` 新建一个 spider（参考 `tencent.py`），保证产出 `JobItem`
- 若为 JS 渲染页面，建议使用站点自身 API，或后续集成 `scrapy-playwright`
- 在 `companies.yml` 补充公司与规模映射

## 法务与合规
- 默认遵守 `robots.txt`，合理设置并发与随机 UA，尊重站点访问频率与条款
- 如站点明确禁止抓取或需要授权，请先获得许可