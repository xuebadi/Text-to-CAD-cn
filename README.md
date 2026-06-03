# 学霸帝 Text-to-CAD

中文文本到CAD模型生成器，基于 build123d 和 OpenCascade。

## 功能特性

- 支持中文自然语言描述生成CAD模型
- 支持8种基础形状：立方体、圆柱、球体、圆锥、圆环、椭球体、棱锥、管道
- 导出标准STEP格式文件
- Web界面和命令行两种使用方式

## 使用方法

### Web界面
双击 启动Web界面.bat 启动Web服务器，浏览器访问 http://localhost:8080

### 命令行
`
学霸帝TextToCAD.exe "生成长100宽200高50的立方体" output.step
`

## 技术栈

- build123d - Python CAD库
- OpenCascade - 底层几何内核
- Python 3.12 (嵌入式版本)

## 版本历史

- v2.0: Web GUI界面，8种CAD形状
- v1.0: 命令行版本，4种基础形状

## License

MIT License
