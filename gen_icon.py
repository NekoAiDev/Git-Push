"""生成 Git Push 工具专属图标 appicon.ico（多尺寸）。

设计：Git 橙渐变圆角方块 + 白色「向上推送箭头 + 分支节点」抽象图形。
- 背景：#FF6B3D -> #D73219 对角渐变，圆角裁切
- 前景：白色主干分支线（带 commit 节点）+ 右侧分叉 + 顶部向上箭头（push）
纯 PIL 绘制，导出 256/128/64/48/32/24/16 多尺寸 ICO。
"""
import os
from PIL import Image, ImageDraw

W = H = 512
WHITE = (255, 255, 255, 255)

# ---- 1) 渐变背景 ----
base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
top = (255, 107, 61)   # FF6B3D
bot = (215, 50, 25)    # D73219
for y in range(H):
    t = y / (H - 1)
    r = int(top[0] * (1 - t) + bot[0] * t)
    g = int(top[1] * (1 - t) + bot[1] * t)
    b = int(top[2] * (1 - t) + bot[2] * t)
    ImageDraw.Draw(base).line([(0, y), (W, y)], fill=(r, g, b, 255))

# ---- 2) 圆角裁切（圆角外透明）----
mask = Image.new("L", (W, H), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, W, H], radius=112, fill=255)
base.putalpha(mask)

d = ImageDraw.Draw(base)
LW = 26  # 线条宽度

def node(cx, cy, rad):
    d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=WHITE)

# ---- 3) 前景：分支 + 推送箭头 ----
# 主干竖线（本地分支主线）
d.line([(210, 410), (210, 160)], fill=WHITE, width=LW)
# 从中间节点向右分叉（feature 分支）
d.line([(210, 275), (380, 275)], fill=WHITE, width=LW)
d.line([(380, 275), (380, 185)], fill=WHITE, width=LW)
node(380, 275, 15)  # 折点圆角过渡
# 顶部向上箭头（push to remote）
d.line([(210, 160), (210, 120)], fill=WHITE, width=LW)
d.line([(168, 170), (210, 120)], fill=WHITE, width=LW)
d.line([(252, 170), (210, 120)], fill=WHITE, width=LW)
# commit 节点（白色圆点）
node(210, 410, 34)
node(210, 275, 34)
node(380, 185, 30)
# 箭头尖与翼端圆润收尾
node(210, 120, 13)
node(168, 170, 13)
node(252, 170, 13)

# ---- 4) 导出多尺寸 ICO ----
sizes = [256, 128, 64, 48, 32, 24, 16]
frames = [base.resize((s, s), Image.LANCZOS) for s in sizes]
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "appicon.ico")
frames[0].save(out, sizes=[(s, s) for s in sizes], append_images=frames[1:])
print("已生成图标:", out, "大小", os.path.getsize(out), "字节")
