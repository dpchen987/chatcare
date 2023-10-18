#!/usr/bin/env python3

import torch

from chatcare.utils.classification_model import EmbeddingClassification
from chatcare.config import params

torch.manual_seed(1258)
model = EmbeddingClassification(
    params.embed_dim, params.num_class_intention)
model.load_state_dict(torch.load(params.classify_intention_path))
model.eval()


def classify(embed):
    '''
    attention: input is embedding of text
    '''
    embed = torch.tensor(embed, dtype=torch.float)
    with torch.no_grad():
        ilabel = model(embed)
    ilabel = int(ilabel.argmax(dim=1)[0])
    return ilabel


