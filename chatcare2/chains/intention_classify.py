#!/usr/bin/env python3
import numpy as np
import onnxruntime as rt
from chatcare2.utils.logger import logger
from chatcare2.config import params

model = rt.InferenceSession(params.classify_intention_path, providers=['CPUExecutionProvider'])
input_name = model.get_inputs()[0].name

def classify(embed):
    '''
    attention: input is embedding of text
    '''
    ilabel = model.run(None, {input_name: embed})[0]
    ilabel = int(np.argmax(ilabel, axis=1)[0])
    logger.info(f"attention id : {ilabel}")
    return str(ilabel)

