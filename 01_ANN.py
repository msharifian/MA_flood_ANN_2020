# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 12:27:59 2020

@author: boehm

"""

import os
import numpy as np
#%%############# Data import #################################################
#import rain array ###########################################################
array_rain_hist = np.load(r'C:\Users\boehm\Google_Drive\Masterarbeit\Part4_ANN_versions\hist_rain_data\dfs0\1_5_factor_13h\final_rain_array\rain_series_hist_1_5.npy')
array_rain_CDS = np.load(r'C:\Users\boehm\Google_Drive\Masterarbeit\Part4_ANN_versions\CDS_rain_data\CDS_rain_series\rain_series_CDS_uneven\rain_series.npy')


#%% import flood arrays #########################################################
##### CDS ################
os.chdir(r'C:\Users\boehm\Google_Drive\Masterarbeit\Part4_ANN_versions\CDS_rain_data\CDS_flood_maps\Numpy-files_CDS_uneven')
path = r'C:\Users\boehm\Google_Drive\Masterarbeit\Part4_ANN_versions\CDS_rain_data\CDS_flood_maps\Numpy-files_CDS_uneven'
files = os.listdir(path)
#print(files)

flood_arrays_CDS = {}

for file in files:
    flood_arrays_CDS[file] = np.load(file)
    
data=list(flood_arrays_CDS.values())
del flood_arrays_CDS, files, file, path
array_flood_CDS = np.asarray(data)
del data

array_flood_CDS = np.reshape(array_flood_CDS,(21,-1))
##### hist #################
os.chdir(r'C:\Users\boehm\Google_Drive\Masterarbeit\Part4_ANN_versions\hist_rain_data\dfs2\1_5_factor_13h\flood_maps')
path = r'C:\Users\boehm\Google_Drive\Masterarbeit\Part4_ANN_versions\hist_rain_data\dfs2\1_5_factor_13h\flood_maps'
files = os.listdir(path)
#print(files)
files = sorted(files, key=lambda item: int(item.split('_')[1].split('.')[0]))

flood_arrays_hist = {}

for file in files:
    flood_arrays_hist[file] = np.load(file)
    
data=list(flood_arrays_hist.values())
del flood_arrays_hist, files, file, path
array_flood_hist = np.asarray(data)
del data
array_flood_hist = np.reshape(array_flood_hist,(24,-1))
#%% zero padding of CDS input
pad_after = np.pad(array_rain_CDS,((0,0),(0,66)),'constant')
# pad_before = np.pad(array_rain_CDS,((0,0),(57,9)),'constant') # 1,5 h buffer before end -> time of concentration
# pad_middle = np.pad(array_rain_CDS,((0,0),(33,33)),'constant')
# pad_before_middle = np.pad(array_rain_CDS,((0,0),(20,46)),'constant')
# pad_after_middle = np.pad(array_rain_CDS,((0,0),(46,20)),'constant')

array_rain_CDS = pad_after
del pad_after
#%% seperate single hist event for prediction, merge CDS and hist events
X = array_rain_CDS
y = array_flood_CDS

X_val = array_rain_hist
y_val = array_flood_hist
# event 4
X_pred_1 = X_val[4]
X_pred_1 = np.reshape(X_pred_1,(1,78))
y_sim_1 = y_val[4]
y_sim_1 = np.reshape(y_sim_1,(1,361315))
# event 11
X_pred_2 = X_val[11]
X_pred_2 = np.reshape(X_pred_2,(1,78))
y_sim_2 = y_val[11]
y_sim_2 = np.reshape(y_sim_2,(1,361315))
# event 16
X_pred_3 = X_val[16]
X_pred_3 = np.reshape(X_pred_3,(1,78))
y_sim_3 = y_val[16]
y_sim_3 = np.reshape(y_sim_3,(1,361315))

X_test = np.concatenate((X_pred_1, X_pred_2, X_pred_3))
y_test = np.concatenate((y_sim_1, y_sim_2, y_sim_3))

X_val = np.delete(X_val,[4,11,16], axis = 0)
y_val = np.delete(y_val,[4,11,16], axis = 0)

del X_pred_1, X_pred_2, X_pred_3, y_sim_1, y_sim_2, y_sim_3, array_flood_CDS, array_flood_hist, array_rain_CDS, array_rain_hist
#%% model
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Dropout
from sklearn import metrics
#from tensorflow.keras.callbacks import EarlyStopping
import matplotlib.pyplot as plt 
#%%
# determine the number of input features:
n_features = X.shape[1] #or X


model = Sequential()
model.add(Dense(78, activation='relu', kernel_initializer='he_normal',
                input_shape=(n_features,)))
model.add(Dropout(0.2))
model.add(Dense(78, activation='tanh', kernel_initializer='he_normal'))
model.add(Dense(361315))


# compile the model:
#optimizer = tf.keras.optimizers.RMSprop(0.001)
optimizer = tf.keras.optimizers.Adam(learning_rate=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-07, amsgrad=False, name='Adam')
model.compile(optimizer=optimizer,loss='mean_squared_error')

# early stopping:
#monitor = EarlyStopping(monitor='val_loss', min_delta=1e-7, patience=10, verbose=1, mode='auto', restore_best_weights=True)
# fit the model:
history = model.fit(X, y,epochs=60, batch_size=32, verbose=1, validation_data = (X_val,y_val))#; callbacks=[monitor]


plt.figure()
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
#plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper left')
plt.show()

# save model

# save model
#model.save(os.path.join(r'C:\Users\boehm\Google_Drive\Masterarbeit\Part4_ANN_versions\ANNs\Models\01_FFNN','model_epochs60_dropout0_2'))

#epoch:iteration over samples;batch_size: total number of training examples present in one batch;verbose:progress bar (off/on)

# evaluate the model:
    #scores = model.evaluate(inputs[test], targets[test], verbose=1)
#%% load model
model = tf.keras.models.load_model(os.path.join(os.path.join(r'C:\Users\boehm\Google_Drive\Masterarbeit\Part4_ANN_versions\ANNs\Models\01_FFNN','model_epochs60_dropout0_2')))
    
#%% prediction 
X_pred1 = X_test[0].reshape(1,78)
y_sim1 = y_test[0].reshape(1,361315)

X_pred2 = X_test[1].reshape(1,78)
y_sim2 = y_test[1].reshape(1,361315)

X_pred3 = X_test[2].reshape(1,78)
y_sim3 = y_test[2].reshape(1,361315)

# make a prediction
yhat1 = model.predict(X_pred1)#
yhat2 = model.predict(X_pred2)
yhat3 = model.predict(X_pred3)

rmse1  = np.sqrt(metrics.mean_squared_error(yhat1, y_sim1))
rmse2  = np.sqrt(metrics.mean_squared_error(yhat2, y_sim2))
rmse3  = np.sqrt(metrics.mean_squared_error(yhat3, y_sim3))

# denormalization
# yhat1 = yhat1 * y_std + y_mean
# y_sim1 = y_sim1 * y_std + y_mean

# yhat2 = yhat2 * y_std + y_mean
# y_sim2 = y_sim2 * y_std + y_mean

# yhat3 = yhat3 * y_std + y_mean
# y_sim3 = y_sim3 * y_std + y_mean


import matplotlib.lines as lines
line = lines.Line2D([0, 1], [0, 1], color='red')

#plot prediction against simulation
fig, ax = plt.subplots(1) #
ax.scatter(yhat1, y_sim1, cmap='Blues')
ax.add_line(line)
plt.xlabel("Prediction")
plt.ylabel("Hydraulic Model")
plt.title('Historical event 14')
plt.show()

#plot prediction and simulation
yhat1_re = np.reshape(yhat1,(569,635))
y_sim1_map = np.reshape(y_sim1,(569,635)) 

yhat2_re = np.reshape(yhat2,(569,635))
y_sim2_map = np.reshape(y_sim2,(569,635)) 

yhat3_re = np.reshape(yhat3,(569,635))
y_sim3_map = np.reshape(y_sim3,(569,635)) 


fig, axs = plt.subplots(2,3)
fig.suptitle('Comparison y_hat and y_true of test events')

im = axs[0, 0].imshow(yhat1_re, cmap='Blues', interpolation='nearest',vmin=0, vmax=1)
axs[0, 0].set_xlabel('Prediction Ev 1')
axs[0, 0].get_xaxis().set_ticks([])
axs[0, 0].get_yaxis().set_ticks([])

axs[1, 0].imshow(y_sim1_map,cmap='Blues', interpolation='nearest',vmin=0, vmax=1)
axs[1, 0].set_xlabel('Simulation Ev 1')
axs[1, 0].get_xaxis().set_ticks([])
axs[1, 0].get_yaxis().set_ticks([])

axs[0, 1].imshow(yhat2_re, cmap='Blues', interpolation='nearest',vmin=0, vmax=1)
axs[0, 1].set_xlabel('Prediction Ev 2')
axs[0, 1].get_xaxis().set_ticks([])
axs[0, 1].get_yaxis().set_ticks([])

axs[1, 1].imshow(y_sim2_map,cmap='Blues', interpolation='nearest',vmin=0, vmax=1)
axs[1, 1].set_xlabel('Simulation Ev 2')
axs[1, 1].get_xaxis().set_ticks([])
axs[1, 1].get_yaxis().set_ticks([])

axs[0, 2].imshow(yhat3_re, cmap='Blues', interpolation='nearest',vmin=0, vmax=1)
axs[0, 2].set_xlabel('Prediction Ev 3')
axs[0, 2].get_xaxis().set_ticks([])
axs[0, 2].get_yaxis().set_ticks([])

axs[1, 2].imshow(y_sim3_map,cmap='Blues', interpolation='nearest',vmin=0, vmax=1)
axs[1, 2].set_xlabel('Simulation Ev 3')
axs[1, 2].get_xaxis().set_ticks([])
axs[1, 2].get_yaxis().set_ticks([])


fig.subplots_adjust(right=0.8)
cbar_ax = fig.add_axes([0.9, 0.15, 0.025, 0.7])
fig.colorbar(im, cax=cbar_ax)

#plt.tight_layout()
plt.show()
#%% save predictions
# link_folder = r'C:\Users\boehm\Google_Drive\Masterarbeit\Part4_ANN_versions\ANNs\Predictions'
# np.save(os.path.join(link_folder,"01_ev1.npy"),yhat1)
# np.save(os.path.join(link_folder,"01_ev2.npy"),yhat2)
# np.save(os.path.join(link_folder,"01_ev3.npy"),yhat3)
#%% for difference maps
difference_1 = y_sim1 - yhat1
difference_2 = y_sim2 - yhat2
difference_3 = y_sim3 - yhat3

link_folder = r'C:\Users\boehm\Google_Drive\Masterarbeit\Part4_ANN_versions\ANNs\Differences'
np.save(os.path.join(link_folder,"01_ep60_difference_ev1.npy"),difference_1)
np.save(os.path.join(link_folder,"01_ep60_difference_ev2.npy"),difference_2)
np.save(os.path.join(link_folder,"01_ep60_difference_ev3.npy"),difference_3)
#%% confusion matrix
 
# create classes for regression output
y_sim1_classes = np.zeros_like(y_sim1)    # initialise a matrix full with zeros
y_sim1_classes[y_sim1 > 0.05] = 1
y_sim1_classes[y_sim1 > 0.1] = 2 
y_sim1_classes[y_sim1 > 0.25] = 3
y_sim1_classes[y_sim1 > 0.5] = 4
y_sim1_classes[y_sim1 > 1] = 5
y_sim1_classes = np.reshape(y_sim1_classes,(361315,-1))

yhat1_classes = np.zeros_like(yhat1)
yhat1_classes[yhat1 > 0.05] = 1
yhat1_classes[yhat1 > 0.1] = 2
yhat1_classes[yhat1 > 0.25] = 3
yhat1_classes[yhat1 > 0.5] = 4
yhat1_classes[yhat1 > 1] = 5
yhat1_classes = np.reshape(yhat1_classes,(361315,-1))
### event 2
y_sim2_classes = np.zeros_like(y_sim2)    # initialise a matrix full with zeros
y_sim2_classes[y_sim2 > 0.05] = 1
y_sim2_classes[y_sim2 > 0.1] = 2 
y_sim2_classes[y_sim2 > 0.25] = 3
y_sim2_classes[y_sim2 > 0.5] = 4
y_sim2_classes[y_sim2 > 1] = 5
y_sim2_classes = np.reshape(y_sim2_classes,(361315,-1))

yhat2_classes = np.zeros_like(yhat2)
yhat2_classes[yhat2 > 0.05] = 1
yhat2_classes[yhat2 > 0.1] = 2
yhat2_classes[yhat2 > 0.25] = 3
yhat2_classes[yhat2 > 0.5] = 4
yhat2_classes[yhat2 > 1] = 5
yhat2_classes = np.reshape(yhat2_classes,(361315,-1))
### event 3
y_sim3_classes = np.zeros_like(y_sim1)    # initialise a matrix full with zeros
y_sim3_classes[y_sim3 > 0.05] = 1
y_sim3_classes[y_sim3 > 0.1] = 2 
y_sim3_classes[y_sim3 > 0.25] = 3
y_sim3_classes[y_sim3 > 0.5] = 4
y_sim3_classes[y_sim3 > 1] = 5
y_sim3_classes = np.reshape(y_sim3_classes,(361315,-1))

yhat3_classes = np.zeros_like(yhat3)
yhat3_classes[yhat3 > 0.05] = 1
yhat3_classes[yhat3 > 0.1] = 2
yhat3_classes[yhat3 > 0.25] = 3
yhat3_classes[yhat3 > 0.5] = 4
yhat3_classes[yhat3 > 1] = 5
yhat3_classes = np.reshape(yhat3_classes,(361315,-1))


# confusion matrix for all values
matrix_con1 = metrics.confusion_matrix(y_sim1_classes,yhat1_classes,labels=[0,1,2,3,4,5])
matrix_con2 = metrics.confusion_matrix(y_sim2_classes,yhat2_classes,labels=[0,1,2,3,4,5])
matrix_con3 = metrics.confusion_matrix(y_sim3_classes,yhat3_classes,labels=[0,1,2,3,4,5])
# confusion matrix for values above 1 cm
#matrix_con_without_0 = metrics.confusion_matrix(y_sim_classes,yhat_classes,labels=[1,2,3,4,5])
# display 
#cm_display = metrics.ConfusionMatrixDisplay(matrix_con,display_labels=[0,1,2,3,4,5]).plot(2)

# y_sim_classes_map = np.reshape(y_sim_classes,(569,635))
# plt.figure(14) #simulation
# plt.imshow(y_sim_classes_map,cmap='Greys',vmin=0, vmax=5)
# plt.colorbar()
# plt.title('y_sim_classes_map')
# plt.show()

# yhat_classes_map = np.reshape(yhat_classes,(569,635))
# plt.figure(15) #prediction
# plt.imshow(yhat_classes_map,cmap='Greys',vmin=0, vmax=5)
# plt.colorbar()
# plt.title('yhat_classes_map')
# plt.show()

misses1 = sum(matrix_con1[:,0])-matrix_con1[0,0]
false_alarm1 = sum(matrix_con1[0])-matrix_con1[0,0]
hits1 = matrix_con1.sum()-misses1-false_alarm1-matrix_con1[0,0]

misses2 = sum(matrix_con2[:,0])-matrix_con2[0,0]
false_alarm2 = sum(matrix_con2[0])-matrix_con2[0,0]
hits2 = matrix_con2.sum()-misses2-false_alarm2-matrix_con2[0,0]

misses3 = sum(matrix_con3[:,0])-matrix_con3[0,0]
false_alarm3 = sum(matrix_con3[0])-matrix_con3[0,0]
hits3 = matrix_con3.sum()-misses3-false_alarm3-matrix_con3[0,0]


csi_value1 =  hits1/(hits1+misses1+false_alarm1)#does not take into account different depths
csi_value2 =  hits2/(hits2+misses2+false_alarm2)
csi_value3 =  hits3/(hits3+misses3+false_alarm3)
#%% Hit-miss map
# differenz in models
#y_diff = y_sim_classes_map - yhat_classes_map

# plt.figure(16) #simulation
# plt.imshow(y_diff,cmap='Greys',vmin=0, vmax=5)
# plt.colorbar()
# plt.title('y_diff_map')
# plt.show()


# create hit miss matrix

y_diff_1 = np.zeros_like(y_sim1_classes)  
y_diff_1 = np.where(np.logical_and(y_sim1_classes == 0, yhat1_classes == 0),1,y_diff_1) #no flooding in both models
y_diff_1 = np.where(np.logical_and(y_sim1_classes > 0, yhat1_classes > 0),2,y_diff_1) #HIT: flooding in both models
y_diff_1 = np.where(np.logical_and(y_sim1_classes > 0, yhat1_classes == 0),3,y_diff_1) #MISS: flooding in hydraulic but not in yhat
y_diff_1 = np.where(np.logical_and(y_sim1_classes == 0, yhat1_classes > 0),4,y_diff_1) #FALSE POSITIVE: flooding in yhat but not in hydraulic
y_diff_2 = np.zeros_like(y_sim2_classes)  
y_diff_2 = np.where(np.logical_and(y_sim2_classes == 0, yhat2_classes == 0),1,y_diff_2) 
y_diff_2 = np.where(np.logical_and(y_sim2_classes > 0, yhat2_classes > 0),2,y_diff_2) 
y_diff_2 = np.where(np.logical_and(y_sim2_classes > 0, yhat2_classes == 0),3,y_diff_2) 
y_diff_2 = np.where(np.logical_and(y_sim2_classes == 0, yhat2_classes > 0),4,y_diff_2)

y_diff_3 = np.zeros_like(y_sim3_classes)  
y_diff_3 = np.where(np.logical_and(y_sim3_classes == 0, yhat3_classes == 0),1,y_diff_3) 
y_diff_3 = np.where(np.logical_and(y_sim3_classes > 0, yhat3_classes > 0),2,y_diff_3) 
y_diff_3 = np.where(np.logical_and(y_sim3_classes > 0, yhat3_classes == 0),3,y_diff_3) 
y_diff_3 = np.where(np.logical_and(y_sim3_classes == 0, yhat3_classes > 0),4,y_diff_3)


from matplotlib.colors import ListedColormap
import seaborn as sns
y_diff_1_map = np.reshape(y_diff_1,(569,635))
y_diff_2_map = np.reshape(y_diff_2,(569,635))
y_diff_3_map = np.reshape(y_diff_3,(569,635))

cmap = ListedColormap(["whitesmoke", "green", "red", "gold"])



fig = plt.figure(figsize=(14,5))
ax1 = fig.add_subplot(131)
ax1.set_title('Hit-miss map test event 1')

ax2 = fig.add_subplot(132)
ax2.set_title('Hit-miss map test event 2')

ax3 = fig.add_subplot(133)
ax3.set_title('Hit-miss map test event 3')


sns.heatmap(y_diff_1_map, ax = ax1, cmap=cmap,yticklabels=False,xticklabels=False,cbar=False)
sns.heatmap(y_diff_2_map, ax = ax2, cmap=cmap,yticklabels=False,xticklabels=False,cbar=False)
sns.heatmap(y_diff_3_map, ax = ax3, cmap=cmap,yticklabels=False,xticklabels=False,cbar=False)
fig.tight_layout()
plt.show()

#%% save hit-miss
# link_folder = r'C:\Users\boehm\Google_Drive\Masterarbeit\Part4_ANN_versions\ANNs\hit-miss'
# np.save(os.path.join(link_folder,"01_ep60_hit_miss_ev1.npy"),y_diff_1_map)
# np.save(os.path.join(link_folder,"01_ep60_hit_miss_ev2.npy"),y_diff_2_map)
# np.save(os.path.join(link_folder,"01_ep60_hit_miss_ev3.npy"),y_diff_3_map)


#%% 2D histogram
yhat1 = np.reshape(yhat1, (361315)) 
y_sim1 = np.reshape(y_sim1, (361315)) 
yhat2 = np.reshape(yhat2, (361315)) 
y_sim2 = np.reshape(y_sim2, (361315)) 
yhat3 = np.reshape(yhat3, (361315)) 
y_sim3 = np.reshape(y_sim3, (361315)) 
#plt.hist2d(yhat2, y_sim2, bins=(300, 300), cmap=plt.cm.jet, range = [[0.05, 1], [0.05, 1]],cmin = 0.05)
#plt.show()
def abline(slope, intercept):
    """Plot a line from slope and intercept"""
    axes = plt.gca()
    x_vals = np.array(axes.get_xlim())
    y_vals = intercept + slope * x_vals
    plt.plot(x_vals, y_vals, '--')

from matplotlib.colors import LogNorm
def histofhist(x, y, ax, ax_histx, ax_histy):
    # no labels
    ax_histx.tick_params(axis="x")#, labelbottom=False)
    ax_histy.tick_params(axis="y")#, labelleft=False)

    # the scatter plot:
    histhist = ax.hist2d(x, y, cmap='jet', bins=(300, 300), range = [[0.0, 1.5], [0.0, 1.5]],norm=LogNorm())
    ax.set_xlabel('Prediction in m')
    ax.set_ylabel('Simulation in m')
    fig.colorbar(histhist[3],ax=ax, location='right', shrink=0.6)

    # now determine nice limits by hand:
    binwidth = 0.02
    xymax = max(np.max(np.abs(x)), np.max(np.abs(y)))
    lim = (int(xymax/binwidth) + 1) * binwidth

    bins = np.arange(-lim, lim + binwidth, binwidth)
    ax_histx.hist(x, bins=bins, log=True)
    ax_histx.set_title('Histogram of prediction')
    #ax_histx.set_ylim([0,50000])
    ax_histx.set_ylabel('No. of cells')
    
    ax_histy.hist(y, bins=bins, orientation='horizontal', log=True)
    ax_histy.set_title('Histogram of simulation')
    #ax_histy.set_xlim([0,50000])
    ax_histy.set_xlabel('No. of cells')
    
# definitions for the axes
left, width = 0.1, 0.65
bottom, height = 0.1, 0.65
spacing = 0.04


rect_scatter = [left, bottom, width, height]
rect_histx = [left, bottom + height + spacing, width-0.13, 0.15]
rect_histy = [left + width + spacing-0.05, bottom, 0.15, height]

# start with a square Figure
fig = plt.figure(figsize=(10, 8))
plt.tight_layout(pad = 0.1)
ax = fig.add_axes(rect_scatter)
ax_histx = fig.add_axes(rect_histx, sharex=ax)
ax_histy = fig.add_axes(rect_histy, sharey=ax)

# use the previously defined function
histofhist(yhat3, y_sim3, ax, ax_histx, ax_histy)

fig.savefig(r'C:\Users\boehm\Google_Drive\Masterarbeit\Part4_ANN_versions\ANNs\Models\01_FFNN\hist_event3',dpi=300)
plt.show()

