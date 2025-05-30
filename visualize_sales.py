import matplotlib.pyplot as plt
import numpy as np

# 年度销量数据
years = [2022, 2023, 2024, 2025]
sales_1 = [2055.15, 3412.97, 4516.93, 5816.29]  # 零基础学机器学习
sales_2 = [3960.88, 3185.75, 1724.19, 2096.24]  # 数据分析咖哥十话
sales_3 = [4162.33, 5439.78, 6773.54, 7850.36]  # GPT图解

labels = ['零基础学机器学习', '数据分析咖哥十话', 'GPT图解']

x = np.arange(len(years))  # 年份位置
width = 0.25  # 柱宽

fig, ax = plt.subplots(figsize=(10, 6))
rects1 = ax.bar(x - width, sales_1, width, label=labels[0])
rects2 = ax.bar(x, sales_2, width, label=labels[1])
rects3 = ax.bar(x + width, sales_3, width, label=labels[2])

# 添加标签和标题
ax.set_xlabel('年份')
ax.set_ylabel('销量')
ax.set_title('年度图书销量')
ax.set_xticks(x)
ax.set_xticklabels(years)
ax.legend()

# 显示数值
for rects in [rects1, rects2, rects3]:
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height:.0f}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.show() 