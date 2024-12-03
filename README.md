# Book Review System

一个基于 Flask 的图书评价系统，允许用户浏览书籍、发表评论、进行互动。

## 功能特点

- 用户认证系统（注册、登录、权限管理）
- 书籍管理（浏览、搜索、添加、编辑、删除）
- 评论系统（评分、评论、回复）
- 互动功能（点赞、举报）
- 管理员功能（内容管理、举报处理）
- 响应式界面设计

## 系统要求

- Python 3.8+
- MySQL 5.7+
- pip（Python 包管理器）

## 安装步骤

1. 克隆仓库：
   ```bash
   git clone <repository-url>
   cd book-review
   ```

2. 创建并激活虚拟环境：
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/MacOS
   source venv/bin/activate
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

4. 配置数据库：
   - 创建 MySQL 数据库
   - 复制 `config.example.py` 为 `config.py`
   - 修改数据库配置信息
   ```bash
   mysql -u root -p
   CREATE DATABASE book_review CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

5. 初始化数据库：
   - 使用 `database.sql` 创建表结构
   ```bash
   mysql -u your-username -p book_review < database.sql
   ```

## 运行应用

1. 启动开发服务器：
   ```bash
   python run.py
   ```

2. 访问应用：
   - 打开浏览器访问 `http://localhost:5000`
   - 默认管理员账户：
     - 邮箱：admin@example.com
     - 密码：admin123

## 项目结构

```
book-review/
├── app/
│   ├── models/         # 数据模型
│   ├── routes/         # 路由处理
│   ├── static/         # 静态文件
│   ├── templates/      # 模板文件
│   └── __init__.py     # 应用初始化
├── database.sql        # 数据库结构
├── config.example.py   # 配置模板
├── requirements.txt    # 依赖列表
└── run.py             # 启动脚本
```

## 使用说明

### 普通用户

1. 注册/登录：
   - 点击导航栏的"Register"注册新账户
   - 使用邮箱和密码登录

2. 浏览书籍：
   - 在首页查看最新和最受欢迎的书籍
   - 使用搜索功能查找特定书籍
   - 点击书籍查看详细信息

3. 评论互动：
   - 对书籍进行评分和评论
   - 回复其他用户的评论
   - 点赞有用的评论
   - 举报不当评论

### 管理员

1. 书籍管理：
   - 添加新书籍
   - 编辑现有书籍信息
   - 删除书籍

2. 内容管理：
   - 处理用户举报
   - 删除不当评论
   - 管理用户账户

## 安全注意事项

1. 生产环境部署：
   - 使用环境变量设置敏感配置
   - 启用 HTTPS
   - 设置强密码策略

2. 数据库安全：
   - 定期备份数据
   - 限制数据库访问权限
   - 使用安全的连接方式

## 故障排除

1. 数据库连接问题：
   - 检查数据库配置信息
   - 确保 MySQL 服务正在运行
   - 验证用户权限

2. 依赖安装问题：
   - 确保 Python 版本兼容
   - 检查系统依赖是否完整
   - 尝试使用 `pip install --upgrade pip`

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。
