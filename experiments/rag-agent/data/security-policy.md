---
document_id: SEC-DATA
title: Data Security Policy
version: 2026.2
effective_date: 2026-02-10
status: current
---

# Data Security Policy

## SEC-TRANSFER 数据传输

production log、customer data 和 access credential 不得发送到私人邮箱或个人云盘。需要外发调试材料时，应先完成脱敏并使用公司批准的传输渠道。

## SEC-VENDOR 第三方访问

vendor 在签约前需要完成 Security review，只要其服务会存储、处理或访问 customer data。采购金额较小也不能跳过这项检查。

## SEC-SECRETS 凭据

共享 credential 必须存放在公司 password manager 中。聊天记录、工单正文和代码仓库都不能用来保存 secret。
