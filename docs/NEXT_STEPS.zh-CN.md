# 后续开发顺序

1. 先运行本地模式：上传 examples/project-notes.txt，测试有证据回答、无证据回答、删除与刷新。
2. 加真实账号登录和服务间认证；当前 cookie 只区分本地浏览器，不是生产登录。
3. 接 PDF/DOCX 加载器，增加文件验证、解析隔离和上传配额。
4. 选择 embedding 模型并配置 Pinecone，验证 namespace、向量维度、文档删除和检索效果。
5. 接 Google ADK 模型与 Runner，加入自定义编排与带来源引用的生成式回答。
6. 接完整 AG-UI/CopilotKit runtime，再加入经过允许的 MCP 外部工具和 web search。
7. 用小型评测集检查检索、引用、拒答、跨用户隔离和提示注入，再部署。

不要把当前关键词检索演示写成已完成的混合向量检索或完整 AI Agent。
