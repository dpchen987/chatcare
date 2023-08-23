from torch import nn


class EmbeddingClassification(nn.Module):
    def __init__(self, embed_dim, num_class):
        super().__init__()
        step = embed_dim // 3
        self.dropout = nn.Dropout(0.10)
        self.softmax = nn.Softmax(dim=1)
        self.fc1 = nn.Linear(embed_dim, step)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(step, num_class)
        self.init_weights()

    def init_weights(self):
        initrange = 0.5
        self.fc1.weight.data.uniform_(-initrange, initrange)
        self.fc1.bias.data.zero_()
        self.fc2.weight.data.uniform_(-initrange, initrange)
        self.fc2.bias.data.zero_()

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        x = self.softmax(x)
        return x
