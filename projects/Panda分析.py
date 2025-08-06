import pandas as pd

# 读取数据
df = pd.read_csv("server_metrics.csv")

# 按 server_id 分组，计算平均CPU使用率
result = df.groupby("timestamp")["cpu_usage"].mean()
print(result)
