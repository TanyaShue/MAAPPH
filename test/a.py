import cv2
import numpy as np

# 定义图片路径
image_paths = [
    '1.png',  # 第一张图片路径
    '2.png'   # 第二张图片路径
]

def calculate_hsv_bounds(image_path):
    """
    计算图片的HSV颜色范围（最小值、平均值和最大值）。
    """
    # 读取图片
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"无法加载路径为 '{image_path}' 的图片。")

    # 将图片转换为HSV色彩空间
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 分别计算H、S、V三个通道的最小值、平均值和最大值
    h_flat, s_flat, v_flat = hsv[:, :, 0].flatten(), hsv[:, :, 1].flatten(), hsv[:, :, 2].flatten()
    min_hsv = [int(np.min(h_flat)), int(np.min(s_flat)), int(np.min(v_flat))]
    mean_hsv = [int(np.mean(h_flat)), int(np.mean(s_flat)), int(np.mean(v_flat))]
    max_hsv = [int(np.max(h_flat)), int(np.max(s_flat)), int(np.max(v_flat))]

    return min_hsv, mean_hsv, max_hsv

# 计算每张图片的HSV范围
results = []
for path in image_paths:
    results.append(calculate_hsv_bounds(path))

# 打印结果
for i, (min_hsv, mean_hsv, max_hsv) in enumerate(results):
    print(f"图片{i+1} ({image_paths[i]}):")
    print(f"  最小HSV值: {min_hsv}")
    print(f"  平均HSV值: {mean_hsv}")
    print(f"  最大HSV值: {max_hsv}\n")