---
document_id: ENG-HANDBOOK
title: Engineering Handbook
version: 2026.3
effective_date: 2026-03-15
status: current
---

# Engineering Handbook

## ENG-DEPLOY Production deployment

production deployment 必须通过 CI，并由两名工程师批准，其中一人不能是该变更的作者。紧急修复可以在事故频道完成第二次批准，但仍要保留记录。

## ENG-INCIDENT SEV-1 incident

SEV-1 incident 处理期间，incident commander 至少每 30 分钟发布一次状态更新。更新应包括用户影响、当前处置和下一次更新时间。

## ENG-LOGS Logging

production log 默认保留 30 天。含有 access token、password 或完整 customer payload 的字段不得写入日志。
