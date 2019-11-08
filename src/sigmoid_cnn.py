# To make RAdam work
import os
os.environ['TF_KERAS']='1'
# RAdam
from keras_radam import RAdam

import numpy as np
np.random.seed(1337)  # for reproducibility

import pandas as pd
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow import keras
import tensorflow_addons as tfa
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten
from tensorflow.keras.layers import Conv2D, MaxPooling2D
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam, SGD, RMSprop
from tensorflow.keras.layers import PReLU, LeakyReLU
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.metrics import Precision, Recall 
from tensorflow.keras.utils import plot_model
from sklearn.metrics import precision_score , recall_score, classification_report, confusion_matrix, roc_auc_score, roc_curve
import tensorflow_addons
from tensorflow_addons.metrics import CohenKappa, F1Score
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras import callbacks

from sklearn.metrics import classification_report, confusion_matrix, roc_curve
from sklearn.model_selection import train_test_split
import PIL
from PIL import Image
from plotter import plot_confusion_matrix

# def create_model(activations, model_name)

if __name__ == "__main__":
    # df = pd.read_csv('data/train_dir_paths/')
    # y = df.pop('target')
    # X = df
    # X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

    # dimensions of our images.
    img_width, img_height = 96, 96
    train_data_dir = 'data/train_images/FOREARM'
    validation_data_dir = 'data/valid_images/FOREARM'
    nb_train_samples = 2272
    nb_validation_samples = 301
    epochs = 20
    batch_size = 20
    model_name = 'sigmoid_cnn_96_forearm'



    model = Sequential()

    model.add(Conv2D(64, (3, 3), input_shape=(img_width, img_height, 3),padding='valid', name = 'first_cnn_layer'))
    model.add(Activation(LeakyReLU(), name = 'first_cnn_activation'))
    model.add(MaxPooling2D(pool_size=(2, 2), name = 'first_pooling_layer'))

    model.add(Conv2D(64, (3, 3) ,padding='same', name = 'first_1_cnn_layer'))
    model.add(Activation('relu', name = 'first_1_cnn_activation'))
    model.add(MaxPooling2D(pool_size=(1, 1), name = 'first_1_pooling_layer'))

    model.add(Conv2D(128, (3, 3), padding='same', name = 'second_cnn_layer'))
    model.add(Activation(LeakyReLU(), name = 'second_cnn_activation'))
    model.add(MaxPooling2D(pool_size=(2, 2), name = 'second_pooling_layer'))

    model.add(Conv2D(128, (3, 3), padding='same', name = 'second_2_cnn_layer'))
    model.add(Activation('relu', name = 'second_2_cnn_activation'))
    model.add(MaxPooling2D(pool_size=(1, 1), name = 'second_2_pooling_layer'))

    model.add(Conv2D(256, (3, 3), padding='same', name = 'third_cnn_layer'))
    model.add(Activation(LeakyReLU(), name = 'third_cnn_activation'))
    model.add(MaxPooling2D(pool_size=(2, 2), name = 'third_pooling_layer'))

    model.add(Conv2D(256, (3, 3), padding='same', name = 'fourth_cnn_layer'))
    model.add(Activation('relu', name = 'fourth_cnn_activation'))
    model.add(MaxPooling2D(pool_size=(2, 2), name = 'fourth_pooling_layer'))

    model.add(Flatten())

    model.add(Dense(64, name = 'first_dense_layer'))
    model.add(Activation(LeakyReLU(), name = 'first_dense_activation'))
    model.add(Dropout(0.1, name = 'first_dense_dropout'))

    model.add(Dense(32, name = 'second_dense_layer'))
    model.add(Activation(LeakyReLU(), name = 'second_dense_activation'))
    model.add(Dropout(0.1, name = 'second_dense_dropout'))

    model.add(Dense(1, name = 'final_sigmoid_layer'))
    model.add(Activation('sigmoid', name = 'sigmoid_activation'))
        
    tensorboard = callbacks.TensorBoard(
    log_dir='logdir',
    histogram_freq=0, 
    write_graph=True,
    update_freq='epoch')

    
    model.compile(loss='binary_crossentropy',optimizer=RAdam(total_steps=10000, warmup_proportion=0.1, min_lr=0.00001),
                metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()])
    # model.load_weights('sigmoid_cnn.h5')
    model.save_weights('data/model_weights/'+model_name+'.h5')
    model.save('data/cnn_models/'+model_name+'.h5')
    
    savename = "{0}_best.h5".format(model_name)

    # this is the augmentation configuration we will use for training
    train_datagen = ImageDataGenerator(
            rotation_range=30,
            width_shift_range=0.1,
            height_shift_range=0.1,
            rescale=1./255,
            shear_range=0.1,
            zoom_range=0.1,
            horizontal_flip=True,
            fill_mode='nearest'
            )

    # this is the augmentation configuration we will use for testing:
    # only rescaling
    test_datagen = ImageDataGenerator(rescale=1. / 255)

    train_generator = train_datagen.flow_from_directory(
    train_data_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode='binary')

    validation_generator = test_datagen.flow_from_directory(
    validation_data_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode='binary',
    shuffle = False)

    mc = callbacks.ModelCheckpoint(
    savename,
    monitor='val_accuracy', 
    verbose=0, 
    save_best_only=True, 
    mode='auto', 
    save_freq='epoch')

    history = model.fit_generator(
    train_generator,
    steps_per_epoch= nb_train_samples // batch_size,
    epochs=epochs,
    validation_data=validation_generator,
    validation_steps=nb_validation_samples // batch_size,
    callbacks=[mc, tensorboard])

    validation_generator.class_indices
    
    # plot loss during training
    fig, ax = plt.subplots(4, figsize = (12, 8))
    ax[0].set_title('Loss')
    ax[0].set_xticks(range(0,epochs+1,1))
    ax[0].plot(history.history['loss'], label='train')
    ax[0].plot(history.history['val_loss'], label='test')
    ax[0].legend()

    i = 6
    # plot accuracy during training
    ax[1].set_xticks(range(0,epochs+1,1))
    ax[1].set_title('Accuracy')
    ax[1].plot(history.history['accuracy'], label='train')
    ax[1].plot(history.history['val_accuracy'], label='test')
    ax[1].legend()

    ax[2].set_xticks(range(0,epochs+1,1))
    ax[2].set_title('Precision')
    ax[2].plot(history.history['precision'], label='train')
    ax[2].plot(history.history['val_precision'], label='test')
    ax[2].legend()

    ax[3].set_xticks(range(0,epochs+1,1))
    ax[3].set_title('Recall')
    ax[3].plot(history.history['recall'], label='train')
    ax[3].plot(history.history['val_recall'], label='test')
    ax[3].legend()

    plt.tight_layout()
    plt.savefig(model_name+'_all_classes.png')

    # Confusion Matrix and Classification Report
    Y_pred = model.predict_generator(validation_generator, nb_validation_samples // batch_size+1)
    y_pred = np.where(Y_pred>=.50, 1, 0)
    print('Confusion Matrix')
    cm = confusion_matrix(validation_generator.classes, y_pred)
    print (cm)

#     plot_confusion_matrix(validation_generator.classes, y_pred)
#     plt.savefig('Capstone3_CM_all_classes_'+str(img_height)+'.png')

    fpr, tpr, thresholds = roc_curve(validation_generator.classes, Y_pred)
    fig, ax = plt.subplots()
    ax.plot(fpr, tpr)
    ax.set_title('ROC - All Classes Positive vs. Negative '+model_name)
    plt.savefig(model_name+'.png')
    
    target_names = ['positive', 'negative']
    print(classification_report(validation_generator.classes, y_pred, target_names=target_names))

    plot_model(model, to_file=model_name+'model_plot.png', show_shapes=True, show_layer_names=True)

    print('AUROC Score')
    print(roc_auc_score(validation_generator.classes, y_pred))
    y_true = validation_generator.classes.reshape(-1,1).flatten()
    y_pred_ck = y_pred.reshape(-1,1).flatten().copy()
    m = tfa.metrics.CohenKappa(num_classes=2)
    m.update_state(y_true, y_pred_ck)
    print('Final result Cohens Kappa: ', m.result().numpy())
    # F1 weighted
#     output = tfa.metrics.F1Score(num_classes=2,average='weighted')
#     output.update_state(y_true, y_pred_ck)
#     print('F1 Weighted score is: ', output.result().numpy()) # 0.6666667

    model.summary()


   