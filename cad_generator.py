#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学霸帝Text-to-CAD CAD生成器
基于build123d实现文本到CAD模型的转换
"""

import build123d as b3d
from build123d import *
import json
from pathlib import Path
import re

class CADGenerator:
    """CAD模型生成器"""
    
    def __init__(self):
        self.supported_shapes = {
            "立方体": self._create_box,
            "方块": self._create_box,
            "长方体": self._create_box,
            "圆柱": self._create_cylinder,
            "圆柱体": self._create_cylinder,
            "球": self._create_sphere,
            "球体": self._create_sphere,
            "圆锥": self._create_cone,
            "圆锥体": self._create_cone,
            "圆环": self._create_torus,
            "环形": self._create_torus,
            "棱柱": self._create_prism,
            "金字塔": self._create_pyramid,
            "棱锥": self._create_pyramid,
            "椭圆": self._create_ellipsoid,
            "椭球": self._create_ellipsoid,
            "六棱柱": self._create_hexagonal_prism,
        }
    
    def parse_description(self, text):
        """解析中文描述文本"""
        text = text.strip()
        
        # 提取尺寸参数
        numbers = re.findall(r'\d+(?:\.\d+)?', text)
        numbers = [float(n) for n in numbers]
        
        # 识别形状类型
        shape_type = None
        for key in self.supported_shapes.keys():
            if key in text:
                shape_type = key
                break
        
        if shape_type is None:
            # 默认创建立方体
            shape_type = "立方体"
        
        return {
            "shape_type": shape_type,
            "numbers": numbers,
            "original_text": text
        }
    
    def generate(self, description, output_file="output.step"):
        """生成CAD模型"""
        print(f"正在解析描述: {description}")
        
        # 解析描述
        parsed = self.parse_description(description)
        shape_type = parsed["shape_type"]
        numbers = parsed["numbers"]
        
        print(f"识别的形状类型: {shape_type}")
        print(f"提取的尺寸参数: {numbers}")
        
        # 生成对应的CAD模型
        if shape_type in self.supported_shapes:
            creator_func = self.supported_shapes[shape_type]
            part = creator_func(numbers)
        else:
            part = self._create_box([])
        
        # 导出为STEP文件
        output_path = Path(output_file)
        self._export_step(part, output_path)
        
        print(f"[成功] CAD模型已生成: {output_path.absolute()}")
        return str(output_path.absolute())
    
    def _create_box(self, numbers):
        """创建立方体/长方体"""
        if len(numbers) >= 3:
            length, width, height = numbers[0], numbers[1], numbers[2]
        elif len(numbers) == 2:
            length, width, height = numbers[0], numbers[1], numbers[1]
        elif len(numbers) == 1:
            length, width, height = numbers[0], numbers[0], numbers[0]
        else:
            length, width, height = 100, 100, 100
        
        print(f"创建立方体: {length} x {width} x {height}")
        
        with BuildPart() as bp:
            Box(length, width, height)
        
        return bp.part
    
    def _create_cylinder(self, numbers):
        """创建圆柱"""
        if len(numbers) >= 2:
            radius = numbers[0] / 2  # 假设第一个数字是直径
            height = numbers[1]
        elif len(numbers) == 1:
            radius = numbers[0] / 2
            height = numbers[0] * 2
        else:
            radius = 25
            height = 100
        
        print(f"创建圆柱: 半径={radius}, 高度={height}")
        
        with BuildPart() as bp:
            Cylinder(radius, height)
        
        return bp.part
    
    def _create_sphere(self, numbers):
        """创建球体"""
        if len(numbers) >= 1:
            radius = numbers[0] / 2
        else:
            radius = 50
        
        print(f"创建球体: 半径={radius}")
        
        with BuildPart() as bp:
            Sphere(radius)
        
        return bp.part
    
    def _create_cone(self, numbers):
        """创建圆锥"""
        if len(numbers) >= 2:
            radius = numbers[0] / 2
            height = numbers[1]
        elif len(numbers) == 1:
            radius = numbers[0] / 2
            height = numbers[0]
        else:
            radius = 25
            height = 100
        
        print(f"创建圆锥: 底面半径={radius}, 高度={height}")
        
        with BuildPart() as bp:
            Cone(radius, height)
        
        return bp.part
    
    def _export_step(self, part, output_path):
        """导出为STEP文件"""
        print(f"导出STEP文件: {output_path}")
        
        # 使用build123d的导出功能
        from build123d import export_step
        export_step(part, str(output_path))
        
        print(f"[成功] STEP文件导出成功")

def main():
    """主函数"""
    generator = CADGenerator()
    
    print("=" * 60)
    print("学霸帝Text-to-CAD CAD生成器")
    print("=" * 60)
    print("\n支持的形状: 立方体/方块/长方体、圆柱/圆柱体、球/球体、圆锥/圆锥体")
    print("尺寸参数: 在描述中包含数字，如'100x200x50的立方体'")
    print("\n示例:")
    print("  - 100x200x50的立方体")
    print("  - 直径80高度150的圆柱")
    print("  - 半径60的球体")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        description = " ".join(sys.argv[1:])
    else:
        description = input("\n请输入CAD模型描述（中文）: ")
    
    output_file = "xuedibai_output.step"
    result = generator.generate(description, output_file)
    
    if result:
        print(f"\n[完成] 成功生成CAD模型!")
        print(f"[文件] 输出文件: {result}")
        print(f"[提示] 可以使用FreeCAD、Fusion360等软件打开STEP文件")
    else:
        print("\n[错误] CAD模型生成失败")
        sys.exit(1)

if __name__ == "__main__":
    import sys
    main()