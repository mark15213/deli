# iOS App

SwiftUI iOS 客户端，提供 Tinder 式卡片复习体验。

## 要求

- Xcode 15+
- iOS 17+
- Swift 5.9+

## 开发

1. 使用 Xcode 打开 `Deli.xcodeproj`
2. 配置开发团队 (Signing & Capabilities)
3. 运行到模拟器或真机

## 架构

```
ios/Deli/
├── App/              # App 入口
├── Features/         # 功能模块
│   ├── Review/       # 复习卡片
│   ├── Dashboard/    # 学习仪表盘
│   └── Settings/     # 设置
├── Core/             # 核心模块
│   ├── Network/      # API 客户端
│   ├── Storage/      # 本地存储
│   └── Models/       # 数据模型
└── UI/               # 通用 UI 组件
```
