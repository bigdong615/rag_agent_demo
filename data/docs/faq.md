# 常见问题 FAQ

## Q1: RockBot 支持私有化部署吗?
支持。Enterprise 版本提供私有化部署方案,可以部署在客户自有的 K8s 集群或裸金属服务器上。

## Q2: 数据是否会上传到第三方?
Standard 和 Pro 版本会通过加密链路调用 Claude API。Enterprise 版本支持完全离线部署,
可对接客户自有的 LLM(如 Llama 3、Qwen)。

## Q3: 如何接入企业现有的知识库?
RockBot 提供 REST API 和 SDK,支持上传 PDF、Word、Markdown、Confluence 导出文件。
索引完成后即可对话检索。

## Q4: 服务等级协议(SLA)是多少?
- Standard:99.5% 可用性
- Pro:99.9% 可用性
- Enterprise:按合同约定,通常 99.95%

## Q5: 是否提供试用?
提供 14 天免费试用,包含 500 次对话额度。
