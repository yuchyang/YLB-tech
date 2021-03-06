from data_preprocess.standardizing import preprocess_df
import pandas as pd
import numpy as np
import torch
import torch.nn.functional as F
from torch.autograd import Variable
import matplotlib.pyplot as plt
import random
from torch.utils.data.dataset import Dataset
from torchvision import transforms
import numpy as np
from utilities import DataLoader, PreProc
import para
from tensorboardX import SummaryWriter


LEARNING_RATE = 0.0001
BATCH_SIZE = 32
EPOCH = 30


class CustomDatasetFromCSV(Dataset):
    def __init__(self, csv_path,transforms=None):

        self.data = preprocess_df(pd.read_csv(csv_path, index_col=0))
        self.labels = np.asarray(self.data).astype(np.float32)
        self.transforms = transforms
        self.size = self.labels.shape[0] * self.labels.shape[1]
        # self.zeros_num = int(self.size * percent)
        # self.ones_num = self.size -  self.zeros_num
        # self.matrix = np.hstack((np.zeros(self.zeros_num)))
        self.train_data = self.labels

    def __getitem__(self, index):
        if self.transforms is not None:
            data = self.transforms(self.data)
        label = self.labels[index]
        return (label, label)

    def __len__(self):
        return len(self.data.index)
class CustomDatasetFromPre(Dataset):
    def __init__(self, data, transforms=None):

        self.data = data
        self.labels = np.asarray(self.data).astype(np.float32)
        self.transforms = transforms
        # self.size = self.data.shape[0] * self.data.shape[1]
        # self.zeros_num = int(self.size * percent)
        # self.ones_num = self.size -  self.zeros_num
        # self.matrix = np.hstack((np.zeros(self.zeros_num)))


    def __getitem__(self, index):
        if self.transforms is not None:
            data = self.transforms(self.data)
        label = self.labels[index]
        return (label, label)

    def __len__(self):
        return len(self.data)

class Net(torch.nn.Module):
    def __init__(self, n_feature, n_hidden, n_output):
        super(Net, self).__init__()
        torch.nn.Dropout(0.1)
        self.hidden = torch.nn.Linear(n_feature, n_hidden)
        self.predict = torch.nn.Linear(n_hidden, n_output)

    def forward(self, x):
        x = F.dropout(x)
        x = F.relu(self.hidden(x))
        x = self.predict(x)
        return x


net2 = torch.nn.Sequential(
    torch.nn.Dropout(0.1),
    torch.nn.Linear(84, 100),
    torch.nn.ReLU(),
    torch.nn.Linear(100, 200),
    torch.nn.ReLU(),
    torch.nn.Linear(200, 100),
    torch.nn.ReLU(),
    torch.nn.Linear(100, 84)
)
net3 = torch.nn.Sequential(
    torch.nn.Dropout(0.1),
    torch.nn.Linear(84, 200),
    torch.nn.ReLU(),
    torch.nn.Linear(200, 500),
    torch.nn.ReLU(),
    torch.nn.Linear(500, 200),
    torch.nn.ReLU(),
    torch.nn.Linear(200, 84)
)


if __name__ == "__main__":
    transformations = transforms.Compose([transforms.ToTensor()])
    dl = DataLoader()
    machine_num = 0 # 0号为001，1号为002，以此类推
    import para
    raw_data = dl(para.train_data,machine_num) #加载数据

    data = raw_data[:,1:] #移除时间列
    pp = PreProc(dl.t[1:])
    pp.fit(data)#预处理
    inputs = pp.transform(data) #预处理输出
    print(np.any(np.isnan(inputs)))#检测是否有NaN
    # custom_data_from_csv = CustomDatasetFromCSV(csv_path='/Users/yangyucheng/Desktop/SCADA/train/201807_1.csv')
    custom_data_from_pre = CustomDatasetFromPre(inputs)
    dataset_loader = torch.utils.data.DataLoader(dataset=custom_data_from_pre,
                                                    batch_size=BATCH_SIZE,
                                                    shuffle=False)

    net = Net(n_feature=84, n_hidden=100, n_output=84)
    optimizer = torch.optim.Adam(net2.parameters(), lr=LEARNING_RATE)
    loss_func = torch.nn.MSELoss()
    plt.ion()
    plt.show()
    writer = SummaryWriter()
    iteration = 0
    for epoch in range(EPOCH):
        for step, (batch_x, batch_y) in enumerate(dataset_loader):
            net2.zero_grad()
            prediction = net2(batch_x)
            loss = loss_func(prediction, batch_y)
            # print('predicion ', prediction[0])
            # print('label ', batch_y[0])
            loss.backward()
            optimizer.step()
            iteration += 1
            print('Epoch: ', epoch, '| Step: ', step, '| Loss', loss)
            writer.add_scalar('data/loss', loss, iteration)
    writer.export_scalars_to_json("./test.json")
    writer.close()
    torch.save(net2, 'net.pkl')
