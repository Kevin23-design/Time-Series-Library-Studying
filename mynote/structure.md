我来帮你分析这个项目的架构并生成一份架构图。首先让我探索项目的核心结构。    

读取 [](file:///d%3A/code/Time-Series-Library/models)
读取 [](file:///d%3A/code/Time-Series-Library/exp)

读取 [](file:///d%3A/code/Time-Series-Library/run.py#1-1)，行 1 到 60
读取 [](file:///d%3A/code/Time-Series-Library/exp/exp_basic.py#1-1)，行 1 到 50

读取 [](file:///d%3A/code/Time-Series-Library/data_provider)
读取 [](file:///d%3A/code/Time-Series-Library/layers)

读取 [](file:///d%3A/code/Time-Series-Library/utils)
现在让我为你生成一份详细的架构图： 

## 项目架构总结
### **Time-Series-Library** 整体架构概览

这是一个**深度学习时间序列基准库**，支持多种预测任务和30+个SOTA模型。架构采用**分层设计**：
#### **核心层级关系：**

1. **输入层** (run.py)
   - 命令行参数解析和配置管理
   - 分发到相应的任务类

2. **任务层** (exp)
   - 6种任务类型：长期预测、短期预测、缺失值插补、分类、异常检测、零样本预测
   - 继承自 `Exp_Basic` 基类，管理模型生命周期（训练/评估/测试）

3. **数据处理层** (data_provider)
   - `data_factory.py` - 根据数据集名称与模式自动加载数据
   - `data_loader.py` - CSV解析、标准化、时间特征编码、创建滑动窗口
   - 支持特殊数据集：M4、UEA等
   - **关键：在此层删除日期列，仅保留7个数值特征**

4. **模型层** (models - 30+模型)
   - 基础模型：DLinear、LightTS
   - Transformer系列：Autoformer、Informer、PatchTST
   - 混合模型：TimesNet、FEDformer、ETSformer、Crossformer
   - 现代模型：Mamba、Moirai、TimesFM、Chronos

5. **神经网络层** (layers)
   - 注意力机制：AutoCorrelation、Fourier Correlation
   - 编码器-解码器架构
   - 分解方法：DWT、MultiWavelet
   - 嵌入和标准化操作

6. **工具层** (utils)
   - 评估指标：MSE、MAE、RMSE、DTW等
   - 损失函数
   - 时间特征编码
   - 数据增强

7. **输出层**
   - 模型检查点保存
   - 实验结果输出

### **关键特性：**
- ✅ **模块化设计**：每个任务/模型独立，易于扩展
- ✅ **自动模型伸缩**：支持30+模型的自动加载
- ✅ **多数据集支持**：20+真实时间序列数据集
- ✅ **完整的数据处理管道**：从CSV到模型输入的全流程

你之前运行的DLinear命令就是在这个架构框架内执行的！
我来帮你分析这个项目的架构并生成一份架构图。首先让我探索项目的核心结构。    

读取 [](file:///d%3A/code/Time-Series-Library/models)

读取 [](file:///d%3A/code/Time-Series-Library/exp)

读取 [](file:///d%3A/code/Time-Series-Library/run.py#1-1)，行 1 到 60

读取 [](file:///d%3A/code/Time-Series-Library/exp/exp_basic.py#1-1)，行 1 到 50

读取 [](file:///d%3A/code/Time-Series-Library/data_provider)

读取 [](file:///d%3A/code/Time-Series-Library/layers)

读取 [](file:///d%3A/code/Time-Series-Library/utils)

现在让我为你生成一份详细的架构图： 



## 项目架构总结

### **Time-Series-Library** 整体架构概览

这是一个**深度学习时间序列基准库**，支持多种预测任务和30+个SOTA模型。架构采用**分层设计**：

#### **核心层级关系：**

1. **输入层** (run.py)
   - 命令行参数解析和配置管理
   - 分发到相应的任务类

2. **任务层** (exp)
   - 6种任务类型：长期预测、短期预测、缺失值插补、分类、异常检测、零样本预测
   - 继承自 `Exp_Basic` 基类，管理模型生命周期（训练/评估/测试）

3. **数据处理层** (data_provider)
   - `data_factory.py` - 根据数据集名称与模式自动加载数据
   - `data_loader.py` - CSV解析、标准化、时间特征编码、创建滑动窗口
   - 支持特殊数据集：M4、UEA等
   - **关键：在此层删除日期列，仅保留7个数值特征**

4. **模型层** (models - 30+模型)
   - 基础模型：DLinear、LightTS
   - Transformer系列：Autoformer、Informer、PatchTST
   - 混合模型：TimesNet、FEDformer、ETSformer、Crossformer
   - 现代模型：Mamba、Moirai、TimesFM、Chronos

5. **神经网络层** (layers)
   - 注意力机制：AutoCorrelation、Fourier Correlation
   - 编码器-解码器架构
   - 分解方法：DWT、MultiWavelet
   - 嵌入和标准化操作

6. **工具层** (utils)
   - 评估指标：MSE、MAE、RMSE、DTW等
   - 损失函数
   - 时间特征编码
   - 数据增强

7. **输出层**
   - 模型检查点保存
   - 实验结果输出

### **关键特性：**
- ✅ **模块化设计**：每个任务/模型独立，易于扩展
- ✅ **自动模型伸缩**：支持30+模型的自动加载
- ✅ **多数据集支持**：20+真实时间序列数据集
- ✅ **完整的数据处理管道**：从CSV到模型输入的全流程

你之前运行的DLinear命令就是在这个架构框架内执行的！