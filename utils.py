import numpy as np
import pandas as pd
import tensorflow as tf
from keras.backend.tensorflow_backend import set_session

from preprocess import preprocess

def limit_gpu_memory(per):
    config = tf.ConfigProto()
    config.gpu_options.per_process_gpu_memory_fraction = per
    set_session(tf.Session(config=config))

    
def train_test_split(data, label, val_size=0.1):
    idx = np.arange(len(data))
    np.random.shuffle(idx)
    split = int(len(data)*val_size)
    x_train, x_test = data[idx[split:]], data[idx[:split]]
    y_train, y_test = label[idx[split:]], label[idx[:split]]
    return x_train, x_test, y_train, y_test


def data_generator(data, labels, max_len = 200000, batch_size=64, shuffle=True):
    idx = np.arange(len(data))
    if shuffle:
        np.random.shuffle(idx)
    batches = [idx[range(batch_size*i, min(len(data), batch_size*(i+1)))] for i in range(len(data)//batch_size+1)]
    while True:
        for i in batches:
            xx = preprocess(data[i], max_len)[0]
            yy = labels[i]
            yield (xx, yy)


class logger():
    def __init__(self):
        self.fn = []
        self.len = []
        self.pad_len = []
        self.loss = []
        self.pred = []
        self.org = []
    def write(self, fn, org_score, file_len, pad_len, loss, pred):
        self.fn.append(fn.split('/')[-1])
        self.org.append(org_score)
        self.len.append(file_len)
        self.pad_len.append(pad_len)
        self.loss.append(loss)
        self.pred.append(pred)
        
        print ('\nFILE:', fn)
        if pad_len > 0:
            print ('\tfile length:', file_len)
            print ('\tpad length:', pad_len)
            if not np.isnan(loss):
                print ('\tloss:', loss)
                print ('\tscore:', pred)
        else:
            print ('\tfile length:', file_len, ', Exceed max length ! Ignored !')
        print ('\toriginal score:', org_score)
        
    def save(self, path):
        d = {'filename':self.fn, 
             'original score':self.org, 
             'file length':self.len,
             'pad length':self.pad_len, 
             'loss':self.loss, 
             'predict score':self.pred}
        df = pd.DataFrame(data=d)
        df.to_csv(path, index=False, columns=['filename','original score', 'file length','pad length','loss','predict score'])
        print ('\nLog saved to "%s"\n' % path)