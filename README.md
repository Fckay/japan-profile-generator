# Japan Profile Generator

一个强大的日本人信息生成 API，可以生成真实可信的日本人档案信息，包括姓名、地址、个人信息等。

## 功能特点

- 生成真实的日本人姓名（平假名、片假名、罗马字）
- 生成符合实际的日本地址信息
- 支持多语言（日文、英文、中文）
- 包含详细的个人信息（年龄、职业、教育背景等）
- RESTful API 设计
- 支持批量生成

## API 端点

- `GET /` - API 状态检查
- `GET /api/generate` - 生成单条随机信息
- `GET /api/generate/batch/<count>` - 批量生成多条信息

## 在线演示

API 地址：[https://jp-api.70tool.com](https://jp-api.70tool.com)

## 本地开发

1. 克隆仓库：