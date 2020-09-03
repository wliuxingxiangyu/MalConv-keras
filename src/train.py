from os.path import join
import argparse
import pickle
import warnings
import pandas as pd
from keras.callbacks import ModelCheckpoint, EarlyStopping
from keras.models import load_model

from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
from tensorflow.keras.models import load_model

import utils
from malconv import Malconv
from preprocess import preprocess

warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser(description='Malconv-keras classifier training')
parser.add_argument('--batch_size', type=int, default=50)
parser.add_argument('--verbose', type=int, default=1)
parser.add_argument('--epochs', type=int, default=100)
parser.add_argument('--limit', type=float, default=0., help="limit gpu memory percentage")
parser.add_argument('--max_len', type=int, default=200000, help="model input legnth")
parser.add_argument('--win_size', type=int, default=500)
parser.add_argument('--val_size', type=float, default=0.2, help="validation percentage")
parser.add_argument('--save_path', type=str, default='../saved/', help='Directory to save model and log')
parser.add_argument('--model_path', type=str, default='../saved/malconv.h5', help="model to resume")
parser.add_argument('--save_best', action='store_true', help="Save model with best validation accuracy")
parser.add_argument('--resume', action='store_true')
parser.add_argument('csv', type=str)



def train(model, max_len=200000, batch_size=50, verbose=True, epochs=100, save_path='../saved/', save_best=True):
    
    # callbacks
    ear = EarlyStopping(monitor='val_acc', patience=5)
    mcp = ModelCheckpoint(join(save_path, 'malconv.h5'), 
                          monitor="val_acc", 
                          save_best_only=save_best, 
                          save_weights_only=False)
    
    # x_train in _main_
    steps_per_epoch_val = len(x_train)//batch_size + 1
    validation_steps_val =  len(x_test)//batch_size + 1

    print("\nlen(x_train):%s, batch_size:%s, steps_per_epoch_val:%s" % (len(x_train), batch_size, steps_per_epoch_val))
    print("len(x_test):%s, validation_steps_val:%s \n" % (len(x_test), validation_steps_val ))
    print("epochs:%s, verbose:%s type(validation_steps_val):%s  \n" % (epochs, verbose, type(validation_steps_val) ))
    
    history = model.fit_generator(
        utils.data_generator(x_train, y_train, max_len, batch_size, shuffle=True),
        steps_per_epoch=steps_per_epoch_val,
        epochs=epochs, 
        verbose=verbose, 
        callbacks=[ear, mcp],
        validation_data=utils.data_generator(x_test, y_test, max_len, batch_size),
        validation_steps=validation_steps_val)
    return history

    
if __name__ == '__main__':
    args = parser.parse_args()
    
    # limit gpu memory
    if args.limit > 0:
        utils.limit_gpu_memory(args.limit)
    
    
    # prepare model
    if args.resume:
        model = load_model(args.model_path)
    else:
        model = Malconv(args.max_len, args.win_size)
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['acc'])
    
    
    # prepare data
    # preprocess is handled in utils.data_generator
    df = pd.read_csv(args.csv, header=None)
    data, label = df[0].values, df[1].values # data is file_path
    x_train, x_test, y_train, y_test = utils.train_test_split(data, label, args.val_size)
    print('hz-------Train on %d samples, test on %d samples' % (len(x_train), len(x_test)))
    
    history = train(model, args.max_len, args.batch_size, args.verbose, args.epochs, args.save_path, args.save_best)
    with open(join(args.save_path, 'history.pkl'), 'wb') as f:
        pickle.dump(history.history, f)

