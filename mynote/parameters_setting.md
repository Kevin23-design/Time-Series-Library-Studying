# Time-Series-Library 超参数设定详细指南

本文面向你当前在 TSLib 的实操场景，目标是：
1. 快速得到一个可跑通、可复现的基线。
2. 用最少试验次数把结果稳步提升。
3. 避免常见的无效调参和资源浪费。

---

## 1. 先建立统一认知：一个样本和一个 batch 是什么

以 ETTh1 多变量预测为例，常见输入张量形状：
- batch_x: (32, 96, 7)
- batch_y: (32, 144, 7)

含义如下：
- 32: batch_size，每步训练同时处理 32 条样本。
- 96: seq_len，编码器输入历史长度。
- 7: 变量数（多变量任务下 ETTh1 的通道数）。

其中 batch_y 的 144 来自：
- label_len + pred_len = 48 + 96 = 144

训练损失通常只计算 pred_len 这段（最后 96 步），label_len 主要是给解码器提供起始上下文。

---

## 2. 参数总览与优先级

### 2.1 最重要的第一层参数（先调这些）

1) 窗口相关
- seq_len: 输入历史窗口长度。
- label_len: 解码器已知上下文长度。
- pred_len: 预测步长。

2) 优化相关
- learning_rate: 学习率。
- train_epochs: 最大训练轮数。
- patience: 早停容忍轮数。
- batch_size: 批大小。

3) 任务定义相关
- features: M / S / MS。
- enc_in, dec_in, c_out: 输入输出通道维度。

### 2.2 第二层参数（模型稳定后再调）

- d_model, d_ff, e_layers, d_layers, n_heads
- dropout
- lradj

### 2.3 第三层参数（细节优化）

- num_workers
- use_amp
- individual（DLinear）
- top_k（TimesNet）

---

## 3. 每个核心参数怎么设

### 3.1 窗口三元组：seq_len / label_len / pred_len

经验规则：
- 先固定 pred_len（任务定义）。
- label_len 常设为 pred_len 的 1/2 或 1 倍。
- seq_len 从 96 起步，再试 192、336、512。

推荐起点：
- 短历史快速基线：seq_len=96, label_len=48, pred_len=96
- 中等历史：seq_len=192, label_len=96, pred_len=96
- 长历史搜索：seq_len=336 或 512, label_len=96, pred_len=96

现象判断：
- 训练/验证都差：可能欠拟合，增大 seq_len 或模型容量。
- 训练好验证差：过拟合，减小容量、增大 dropout、加强早停。

### 3.2 learning_rate

推荐搜索网格：
- 1e-3（偏大，收敛快但易震荡）
- 5e-4
- 1e-4（默认常用）
- 5e-5（偏稳）

经验：
- DLinear 这类轻量模型通常 1e-4 到 5e-4 好用。
- Transformer 类模型常用 1e-4 起步。
- 出现 loss 抖动大、验证不稳时优先降学习率。

### 3.3 batch_size

常用候选：16 / 32 / 64 / 128（受显存约束）

经验：
- batch 大：梯度更平滑，吞吐更高，但泛化不一定更好。
- batch 小：噪声更大，可能泛化更好，但训练更慢。

落地建议：
- 先用 32。
- 显存有余就试 64。
- 对比验证集 MSE，不要只看训练速度。

### 3.4 train_epochs 与 patience

推荐：
- train_epochs: 10 到 30 起步
- patience: 3 到 7

关系：
- train_epochs 是上限。
- patience 控制提前终止，防止无效训练。

### 3.5 d_model / d_ff / e_layers / d_layers / n_heads

建议在基线稳定后再动。

起步建议：
- 轻量实验：d_model=128 或 256, d_ff=512 或 1024
- 常规实验：d_model=512, d_ff=2048

注意：
- d_model 增大显著增加显存和训练时间。
- n_heads 需与 d_model 匹配，保证每头维度合理。

### 3.6 dropout

推荐范围：0.1 到 0.3

经验：
- 小数据、过拟合明显：上调到 0.2 或 0.3。
- 欠拟合：下调到 0.05 或 0.1。

### 3.7 features 与通道参数

- features=M: 多变量输入，多变量输出。
- features=S: 单变量输入，单变量输出。
- features=MS: 多变量输入，单变量输出（target）。

通道建议：
- M: enc_in=变量数, dec_in=变量数, c_out=变量数
- S: enc_in=1, dec_in=1, c_out=1
- MS: enc_in=变量数, dec_in=变量数, c_out=1

---

## 4. 按任务给出可直接使用的起始配置

### 4.1 长期预测（ETTh1，多变量）

基线（你当前路线）
- model: DLinear
- seq_len/label_len/pred_len: 96/48/96
- batch_size: 32
- learning_rate: 1e-4
- train_epochs/patience: 10/3

提升版（先改窗口）
- seq_len: 192 或 336
- 其他参数先不动

再提升（再改模型）
- 尝试 TimesNet、iTransformer
- 保持同一组数据与窗口，公平对比

### 4.2 短期预测

- pred_len 通常更短
- 可先用更小 d_model（例如 64 或 128）做快速对比
- 先锁定窗口与学习率，再微调模型结构

### 4.3 插补任务

- 关键参数：mask_rate
- 常用起点：0.125 或 0.25
- mask_rate 越高任务越难，指标通常更差

### 4.4 异常检测

- 关键参数：anomaly_ratio、win_size、step
- 先保证数据标准化流程一致，再调阈值和窗口

### 4.5 分类任务

- 关键参数：seq_len、d_model、dropout、学习率
- 一般更敏感于数据增强和正则化

---

## 5. 高性价比调参流程（推荐照做）

阶段 A：确定强基线
1. 固定模型（例如 DLinear）和数据集。
2. 固定 pred_len。
3. 运行 96/48/96，记录 val/test MSE、MAE。

阶段 B：只调窗口
1. 只改 seq_len: 96 -> 192 -> 336。
2. 每次只跑 1 到 2 个随机种子。
3. 选最稳的一组进入下一阶段。

阶段 C：只调学习率和 batch
1. lr: 1e-4 -> 5e-4 -> 5e-5。
2. batch: 32 -> 64（若显存允许）。
3. 用同样训练轮数比较验证指标。

阶段 D：再换模型
1. 用阶段 C 最优超参，替换为 TimesNet 或 iTransformer。
2. 只在必要时再调 d_model、d_ff。

---

## 6. 常见问题与处理策略

问题 1：训练 loss 降，验证 loss 不降
- 原因：过拟合。
- 处理：增大 dropout、减小 d_model、减少 epochs、提高早停敏感度。

问题 2：训练和验证都不降
- 原因：欠拟合或学习率不合适。
- 处理：先提高学习率（例如 1e-4 到 5e-4）或增大模型容量。

问题 3：loss 大幅震荡
- 原因：学习率偏高或 batch 太小。
- 处理：降低学习率，或增大 batch_size。

问题 4：显存不够
- 处理顺序：减小 batch_size -> 减小 seq_len -> 关闭不必要模型复杂度。

问题 5：结果波动大
- 处理：固定种子，多跑 3 次取均值，不看单次最好结果。

---

## 7. 实验记录模板（建议每次都填）

实验名称：
- model_id:
- 模型:
- 数据集:

关键超参数：
- seq_len / label_len / pred_len:
- batch_size:
- learning_rate:
- train_epochs / patience:
- d_model / d_ff / e_layers / d_layers:
- dropout:

结果：
- Train Loss:
- Vali Loss:
- Test MSE:
- Test MAE:

结论：
- 本次优于基线的原因：
- 下一步只改哪 1 到 2 个参数：

---

## 8. ETTh1 多变量任务的推荐起跑命令

方案 A：稳妥基线

python -u run.py --task_name long_term_forecast --is_training 1 --root_path ./dataset/ETT-small/ --data_path ETTh1.csv --model_id base_dlinear --model DLinear --data ETTh1 --features M --seq_len 96 --label_len 48 --pred_len 96 --enc_in 7 --dec_in 7 --c_out 7 --batch_size 32 --learning_rate 0.0001 --train_epochs 10 --patience 3 --num_workers 2

方案 B：只拉长历史窗口

python -u run.py --task_name long_term_forecast --is_training 1 --root_path ./dataset/ETT-small/ --data_path ETTh1.csv --model_id longctx_dlinear --model DLinear --data ETTh1 --features M --seq_len 336 --label_len 48 --pred_len 96 --enc_in 7 --dec_in 7 --c_out 7 --batch_size 32 --learning_rate 0.0001 --train_epochs 10 --patience 3 --num_workers 2



---

## 9. 一句话策略总结

先用小步、单因素方式调参：每次只改一个关键参数，优先调窗口和学习率，稳定后再换模型和改结构参数。
