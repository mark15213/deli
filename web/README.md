# Web Admin

Next.js 管理端，用于 Inbox 管理和 Quiz 编辑。

## 要求

- Node.js 20+
- npm 或 pnpm

## 开发

```bash
# 安装依赖
npm install

# 运行开发服务器
npm run dev

# 构建生产版本
npm run build
```

## 架构

```
web/
├── src/
│   ├── app/          # Next.js App Router
│   ├── components/   # React 组件
│   ├── lib/          # 工具函数
│   └── types/        # TypeScript 类型
├── public/           # 静态资源
└── package.json
```
