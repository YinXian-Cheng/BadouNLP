# coding:utf8

import torch
import torch.nn as nn
import numpy as np
import random
import json
import matplotlib.pyplot as plt

"""

基于pytorch框架编写模型训练
实现一个自行构造的找规律(机器学习)任务
规律：x是一个5维向量，最大的数字在哪个维度就属于哪一类。

"""


class TorchModel(nn.Module):
    def __init__(self, input_size):
        super(TorchModel, self).__init__()
        self.linear = nn.Linear(input_size, 5)  # 线性层
        self.loss = nn.CrossEntropyLoss()  # 损失函数采用交叉熵损失

    # 输入真实标签时返回 loss 值；无真实标签返回预测类别概率
    def forward(self, x, y=None):
        y_pred = self.linear(x)
        if y is not None:
            return self.loss(y_pred, y)  # 计算损失
        else:
            return y_pred  # 输出预测结果


# 生成一个样本，样本的生成方法，代表了我们要学习的规律
# 随机生成一个5维向量，最大的数字在哪个维度就认为属于哪一类
def build_sample():
    x = np.random.random(5)
    y = np.argmax(x)  # 返回最大值的索引作为标签
    return x, y


# 随机生成一批样本
def build_dataset(total_sample_num):
    X = []
    Y = []
    for _ in range(total_sample_num):
        x, y = build_sample()
        X.append(x)
        Y.append(y)
    return torch.FloatTensor(X), torch.LongTensor(Y)


# 测试代码
# 用来测试每轮模型的准确率
def evaluate(model):
    model.eval()
    test_sample_num = 100
    x, y = build_dataset(test_sample_num)
    correct, wrong = 0, 0
    with torch.no_grad():
        y_pred = model(x)    #模型预测
        for y_p, y_t in zip(y_pred, y):   #与真实标签预测
            if torch.argmax(y_p) == int(y_t):
                correct += 1
            wrong += 1
    print("正确预测个数：%d, 正确率：%f" % (correct, correct / (correct + wrong)))
    return correct / (correct + wrong)


def main():
    # 配置参数
    epoch_num = 20  # 训练轮数
    batch_size = 30  # 每次训练样本个数
    train_sample = 5000  # 每轮训练总共训练的样本总数
    input_size = 5  # 输入向量维度
    learning_rate = 0.001  # 学习率

    # 建立模型
    model = TorchModel(input_size)

    # 选择优化器
    optim = torch.optim.Adam(model.parameters(), lr=learning_rate)
    log = []

    # 创建训练集，正常任务是读取训练集
    train_x, train_y = build_dataset(train_sample)

    # 训练过程
    for epoch in range(epoch_num):
        model.train()
        watch_loss = []

        for batch_index in range(train_sample // batch_size):
            x = train_x[batch_index * batch_size: (batch_index + 1) * batch_size]
            y = train_y[batch_index * batch_size: (batch_index + 1) * batch_size]
            loss = model(x, y)  # 计算损失
            loss.backward()  # 计算梯度
            optim.step()  # 更新权重
            optim.zero_grad()  # 梯度归零
            watch_loss.append(loss.item())

        print("=========\n第%d轮平均loss:%f" % (epoch + 1, np.mean(watch_loss)))
        acc = evaluate(model)  # 测试本轮模型结果
        log.append([acc, float(np.mean(watch_loss))])

    # 保存模型
    torch.save(model.state_dict(), "model.bin")

    # 画图
    plt.plot(range(len(log)), [l[0] for l in log], label="acc")  # 画 acc 曲线
    plt.plot(range(len(log)), [l[1] for l in log], label="Loss")  # 画 loss 曲线
    plt.legend()
    plt.show()

# 使用训练好的模型做预测
def predict(model_path, input_vec):
    input_size = 5
    model = TorchModel(input_size)
    model.load_state_dict(torch.load(model_path))  # 加载训练好的权重
    print(model.state_dict())

    model.eval()  # 测试模式
    with torch.no_grad():  # 不计算梯度
        result = model.forward(torch.FloatTensor(input_vec))  # 模型预测
    for vec, res in zip(input_vec, result):
        print("输入：%s, 预测类别：%d, 概率值：%f" % (vec, round(float(res)), res))  # 打印结果

if __name__ == "__main__":
    main()
