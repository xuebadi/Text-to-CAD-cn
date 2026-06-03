#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学霸帝Text-to-CAD v2.0 Web界面
基于Flask的CAD生成Web服务
"""
import os
import sys
import io
import re
import json

# 设置便携版Python路径
PYTHON_EMBED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

# 添加路径
if PYTHON_EMBED_DIR not in sys.path:
    sys.path.insert(0, PYTHON_EMBED_DIR)
os.environ["PYTHONPATH"] = PYTHON_EMBED_DIR

# build123d延迟导入
BUILD123D_READY = False
try:
    import build123d as b3d
    from build123d import BuildPart, Box, Cylinder, Sphere, Cone, Torus, export_step
    BUILD123D_READY = True
    print("[OK] build123d loaded")
except ImportError as e:
    print(f"[WARN] build123d not available: {e}")

from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

PORT = 8080

HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>学霸帝 Text-to-CAD v2.0</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); min-height: 100vh; color: #e0e0e0; }
.container { max-width: 900px; margin: 0 auto; padding: 40px 20px; }
h1 { text-align: center; color: #00d4ff; font-size: 2.5em; margin-bottom: 10px; text-shadow: 0 0 20px rgba(0,212,255,0.5); }
.subtitle { text-align: center; color: #888; margin-bottom: 40px; font-size: 1.1em; }
.card { background: rgba(255,255,255,0.05); border-radius: 16px; padding: 30px; margin-bottom: 24px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); }
label { display: block; margin-bottom: 12px; color: #00d4ff; font-weight: 600; font-size: 1.1em; }
textarea { width: 100%; height: 100px; padding: 16px; border-radius: 12px; border: 2px solid rgba(0,212,255,0.3); background: rgba(0,0,0,0.3); color: #fff; font-size: 1.1em; resize: vertical; transition: border-color 0.3s; }
textarea:focus { outline: none; border-color: #00d4ff; box-shadow: 0 0 15px rgba(0,212,255,0.2); }
.preset { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-top: 20px; }
.preset-btn { padding: 10px; border-radius: 8px; border: 1px solid rgba(0,212,255,0.3); background: rgba(0,0,0,0.2); color: #aaa; cursor: pointer; text-align: left; font-size: 0.9em; transition: all 0.2s; }
.preset-btn:hover { background: rgba(0,212,255,0.1); border-color: #00d4ff; color: #fff; }
.btn { width: 100%; padding: 18px; border-radius: 12px; border: none; background: linear-gradient(135deg, #00d4ff, #0099cc); color: #fff; font-size: 1.2em; font-weight: 700; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; margin-top: 16px; }
.btn:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,212,255,0.4); }
.btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
.result { padding: 20px; border-radius: 12px; background: rgba(0,255,136,0.1); border: 1px solid rgba(0,255,136,0.3); color: #00ff88; display: none; margin-top: 16px; }
.result.show { display: block; }
.result.error { background: rgba(255,0,80,0.1); border-color: rgba(255,0,80,0.3); color: #ff5050; }
#status { text-align: center; margin-top: 10px; color: #888; min-height: 24px; }
.shapes-info { margin-top: 30px; padding: 20px; background: rgba(255,255,255,0.03); border-radius: 12px; }
.shapes-info h3 { color: #00d4ff; margin-bottom: 16px; }
.shapes-info ul { list-style: none; }
.shapes-info li { padding: 8px 0; color: #aaa; border-bottom: 1px solid rgba(255,255,255,0.05); }
.shapes-info li:last-child { border-bottom: none; }
.download-btn { display: inline-block; padding: 12px 24px; background: linear-gradient(135deg, #00d4ff, #0099cc); color: #fff; text-decoration: none; border-radius: 8px; font-weight: 600; margin-top: 10px; }
.download-btn:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(0,212,255,0.4); }
</style>
</head>
<body>
<div class="container">
    <h1>[ AI ] 学霸帝 Text-to-CAD</h1>
    <p class="subtitle">基于 build123d + OpenCascade 的智能CAD模型生成工具 v2.0</p>

    <div class="card">
        <label>描述想生成的3D模型（中文）：</label>
        <textarea id="desc" placeholder="例如：100x200x50的立方体"></textarea>
        <div class="preset">
            <button class="preset-btn" onclick="document.getElementById('desc').value='100x200x50的立方体'">立方体 100x200x50</button>
            <button class="preset-btn" onclick="document.getElementById('desc').value='直径80高度150的圆柱'">圆柱 直径80高150</button>
            <button class="preset-btn" onclick="document.getElementById('desc').value='半径60的球体'">球体 半径60</button>
            <button class="preset-btn" onclick="document.getElementById('desc').value='底径100高度80的圆锥'">圆锥 底径100高80</button>
            <button class="preset-btn" onclick="document.getElementById('desc').value='大径80小径20的圆环'">圆环 大80小20</button>
            <button class="preset-btn" onclick="document.getElementById('desc').value='直径60高度100的六棱柱'">六棱柱 直径60高100</button>
            <button class="preset-btn" onclick="document.getElementById('desc').value='底径80高度60的四棱锥'">棱锥 底径80高60</button>
        </div>
    </div>

    <button class="btn" id="generateBtn" onclick="generate()">[ 生成 CAD 模型 ]</button>
    <p id="status"></p>
    <div class="result" id="result"></div>

    <div class="shapes-info">
        <h3>支持的形状类型</h3>
        <ul>
            <li><b>立方体/方块/长方体</b> - 输入: 100x200x50</li>
            <li><b>圆柱/圆柱体</b> - 输入: 直径80高度150</li>
            <li><b>球体/球</b> - 输入: 半径60</li>
            <li><b>圆锥/圆锥体</b> - 输入: 底径100高度80</li>
            <li><b>圆环/甜甜圈</b> - 输入: 大径80小径20</li>
            <li><b>六棱柱</b> - 输入: 直径60高度100</li>
            <li><b>四棱锥/金字塔</b> - 输入: 底径80高度60</li>
        </ul>
        <p style="margin-top:16px;color:#666;font-size:0.9em;">生成后点击"下载STEP文件"保存到本地，可用FreeCAD、Fusion360等软件打开查看。</p>
    </div>
</div>

<script>
let generating = false;
async function generate() {
    if (generating) return;
    const desc = document.getElementById('desc').value.trim();
    if (!desc) { alert('请输入描述'); return; }

    const btn = document.getElementById('generateBtn');
    const status = document.getElementById('status');
    const result = document.getElementById('result');

    btn.disabled = true;
    generating = true;
    status.textContent = '正在生成CAD模型...';
    result.classList.remove('show', 'error');
    result.innerHTML = '';

    try {
        const formData = new FormData();
        formData.append('description', desc);

        const resp = await fetch('/generate', { method: 'POST', body: formData });
        const data = await resp.json();

        if (data.success) {
            result.innerHTML = '[成功] CAD模型已生成！<br><br><a href="/download" class="download-btn">[ 下载 STEP 文件 ]</a><br><br>形状: ' + data.shape + ' | 参数: ' + data.numbers.join(' x ');
            result.classList.add('show');
        } else {
            result.textContent = '[错误] ' + data.error;
            result.classList.add('show', 'error');
        }
    } catch (e) {
        result.textContent = '[错误] ' + e.message;
        result.classList.add('show', 'error');
    } finally {
        btn.disabled = false;
        generating = false;
        status.textContent = '';
    }
}
</script>
</body>
</html>
"""


class CADGenerator:
    """CAD模型生成器"""

    def __init__(self):
        self.shapes = {
            "box": self._box,
            "cylinder": self._cylinder,
            "sphere": self._sphere,
            "cone": self._cone,
            "torus": self._torus,
            "hex": self._hex,
            "pyramid": self._pyramid,
        }

    def parse(self, text):
        """解析中文描述"""
        text = text.strip()
        numbers = re.findall(r'\d+(?:\.\d+)?', text)
        numbers = [float(n) for n in numbers]

        # 识别形状
        if "立方体" in text or "方块" in text or "长方体" in text:
            shape = "box"
        elif "圆柱" in text:
            shape = "cylinder"
        elif "球" in text:
            shape = "sphere"
        elif "圆锥" in text or "锥" in text:
            shape = "cone"
        elif "圆环" in text or "环" in text or "甜甜圈" in text:
            shape = "torus"
        elif "六棱" in text or "棱柱" in text:
            shape = "hex"
        elif "棱锥" in text or "金字塔" in text:
            shape = "pyramid"
        else:
            shape = "box"

        return shape, numbers

    def generate(self, shape, numbers):
        """生成CAD模型"""
        if shape in self.shapes:
            return self.shapes[shape](numbers)
        return self._box([])

    def _box(self, nums):
        if len(nums) >= 3:
            l, w, h = nums[0], nums[1], nums[2]
        elif len(nums) == 2:
            l, w, h = nums[0], nums[1], nums[1]
        elif len(nums) == 1:
            l, w, h = nums[0], nums[0], nums[0]
        else:
            l, w, h = 100, 100, 100
        with BuildPart() as bp:
            Box(l, w, h)
        return bp.part

    def _cylinder(self, nums):
        if len(nums) >= 2:
            d, h = nums[0], nums[1]
            r = d / 2.0
        elif len(nums) == 1:
            d = nums[0]
            r, h = d / 2.0, d * 2
        else:
            r, h = 25, 100
        with BuildPart() as bp:
            Cylinder(r, h)
        return bp.part

    def _sphere(self, nums):
        r = nums[0] / 2.0 if nums else 50
        with BuildPart() as bp:
            Sphere(r)
        return bp.part

    def _cone(self, nums):
        if len(nums) >= 2:
            r, h = nums[0] / 2.0, nums[1]
        elif len(nums) == 1:
            r, h = nums[0] / 2.0, nums[0]
        else:
            r, h = 25, 100
        with BuildPart() as bp:
            Cone(r, h)
        return bp.part

    def _torus(self, nums):
        if len(nums) >= 2:
            R, r = nums[0] / 2.0, nums[1] / 2.0
        elif len(nums) == 1:
            R, r = nums[0] / 2.0, nums[0] / 8.0
        else:
            R, r = 50, 10
        with BuildPart() as bp:
            Torus(R, r)
        return bp.part

    def _hex(self, nums):
        if len(nums) >= 2:
            d, h = nums[0], nums[1]
            r = d / 2.0
        elif len(nums) == 1:
            r, h = nums[0] / 2.0, nums[0] * 1.5
        else:
            r, h = 30, 80
        with BuildPart() as bp:
            Cylinder(r, h, n_sides=6)
        return bp.part

    def _pyramid(self, nums):
        if len(nums) >= 2:
            d, h = nums[0], nums[1]
            r = d / 2.0
        elif len(nums) == 1:
            r, h = nums[0] / 2.0, nums[0] * 1.2
        else:
            r, h = 40, 60
        with BuildPart() as bp:
            Cone(r, h, n_sides=4)
        return bp.part


class Handler(SimpleHTTPRequestHandler):
    """HTTP请求处理器"""

    def __init__(self, *args, **kwargs):
        # 设置目录
        self.directory = os.path.dirname(os.path.abspath(__file__))
        super().__init__(*args, directory=self.directory, **kwargs)

    def do_GET(self):
        """处理GET请求"""
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(HTML.encode('utf-8')))
            self.end_headers()
            self.wfile.write(HTML.encode('utf-8'))
        elif self.path == '/download':
            # 下载STEP文件
            step_file = os.path.join(self.directory, 'web_output.step')
            if os.path.exists(step_file):
                with open(step_file, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/octet-stream')
                self.send_header('Content-Disposition', 'attachment; filename=cad_model.step')
                self.send_header('Content-Length', len(content))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404, 'File not found')
        else:
            super().do_GET()

    def do_POST(self):
        """处理POST请求 - 生成CAD模型"""
        if self.path == '/generate':
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length).decode('utf-8')
                params = urllib.parse.parse_qs(post_data)
                description = params.get('description', [''])[0]
            else:
                description = ''

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()

            try:
                if not BUILD123D_READY:
                    self.wfile.write(json.dumps({
                        "success": False,
                        "error": "build123d not available"
                    }).encode('utf-8'))
                    return

                # 生成CAD
                gen = CADGenerator()
                shape, numbers = gen.parse(description)
                part = gen.generate(shape, numbers)

                # 保存STEP文件
                output_path = os.path.join(self.directory, 'web_output.step')
                export_step(part, output_path)

                self.wfile.write(json.dumps({
                    "success": True,
                    "shape": shape,
                    "numbers": numbers,
                    "filename": "cad_model.step"
                }).encode('utf-8'))

            except Exception as e:
                import traceback
                traceback.print_exc()
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": str(e)
                }).encode('utf-8'))
        else:
            self.send_error(404)


def main():
    """启动Web服务器"""
    print("=" * 50)
    print("学霸帝 Text-to-CAD v2.0 Web界面")
    print("=" * 50)
    print(f"\n启动服务器: http://localhost:{PORT}")
    print("按 Ctrl+C 停止服务器\n")

    server = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f"[OK] 服务器运行中: http://localhost:{PORT}")
    print("[OK] 打开浏览器访问")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] 服务器已停止")
        server.shutdown()


if __name__ == '__main__':
    main()
