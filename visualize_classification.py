# Instant Recognition with Caffe

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# Make sure that caffe is on the python path:
caffe_root = '../'  # this file is expected to be in {caffe_root}/examples
import sys
sys.path.insert(0, caffe_root + 'python')
import caffe
import os
#############################################
# iCubWorld28 or DATASET
MODEL = 'iCubWorld28"
# object, attribute_X, affordance
MODEL_TYPE = 'object'

if MODEL == 'DATASET':
	if MODEL_TYPE == 'object':
		dataset = "DATASET"
		model = "bvlc_reference_caffenet_DATASET/object"
		trained = "caffenet_train_iter_10000.caffemodel"
		mean_file = "DATASET_mean.npy"
		labels_file = 'data/DATASET/synsets.txt'
	elif MODEL_TYPE == 'attribute_shape':
	elif MODEL_TYPE == 'attribute_material':
	elif MODEL_TYPE == 'attribute_color':
	elif MODEL_TYPE == 'affordance':
	else:
		print "Wrong MODEL_TYPE set!"

elif MODEL == 'iCubWorld28':
	if MODEL_TYPE == 'object':
		dataset = "iCubWorld28"
		model = "bvlc_reference_caffenet_iCubWorld28/object"
		trained = "caffenet_object.caffemodel"
		mean_file = "iCubWorld_mean.npy"
		labels_file = 'data/DATASET/synsets.txt'
	elif MODEL_TYPE == 'attribute_shape':
	elif MODEL_TYPE == 'attribute_material':
	elif MODEL_TYPE == 'attribute_color':
	elif MODEL_TYPE == 'affordance':
	else:
		print "Wrong MODEL_TYPE set!"
else:
	print "Wrong MODEL set!"


#############################################



plt.rcParams['figure.figsize'] = (10, 10)
plt.rcParams['image.interpolation'] = 'nearest'
plt.rcParams['image.cmap'] = 'gray'

caffe.set_device(0)
caffe.set_mode_gpu()
#net = caffe.Net(caffe_root + 'models/bvlc_reference_caffenet/deploy.prototxt',
#                caffe_root + 'models/bvlc_reference_caffenet/bvlc_reference_caffenet.caffemodel',
#                caffe.TEST)



net = caffe.Net(caffe_root + 'models/' + model + '/deploy.prototxt',
                caffe_root + 'models/' + model + '/' + trained,
                caffe.TEST)

# input preprocessing: 'data' is the name of the input blob == net.inputs[0]
transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
transformer.set_transpose('data', (2,0,1))
transformer.set_mean('data', np.load(caffe_root + 'python/caffe/imagenet/DATASET_mean.npy').mean(1).mean(1)) # mean pixel
transformer.set_raw_scale('data', 255)  # the reference model operates on images in [0,255] range instead of [0,1]
transformer.set_channel_swap('data', (2,1,0))  # the reference model has channels in BGR order instead of RGB

# set net to batch size of 50
net.blobs['data'].reshape(50,3,227,227)

#net.blobs['data'].data[...] = transformer.preprocess('data', caffe.io.load_image(caffe_root + 'examples/images/cat.jpg'))
net.blobs['data'].data[...] = transformer.preprocess('data', caffe.io.load_image('/home/icub-niklas/Desktop/DATASET/train/day1/Sponge/00000177.ppm'))

out = net.forward()
print("Predicted class is #{}.".format(out['prob'][0].argmax()))

plt.imshow(transformer.deprocess('data', net.blobs['data'].data[0]))
plt.show()

# load labels
imagenet_labels_filename = caffe_root + 'data/DATASET/objects/synsets_object.txt'
try:
    labels = np.loadtxt(imagenet_labels_filename, str, delimiter='\t')
except:
    print "Labels not found"

# sort top k predictions from softmax output
#top_k = net.blobs['prob'].data[0].flatten().argsort()[-1:-6:-1]
top_k = net.blobs['prob'].data[0].flatten().argsort()[-1:-6:-1]
top_1 = net.blobs['prob'].data[0].flatten().argsort()[-1]
print labels[top_k]
print labels[top_1]

### Layer features and shapes
[(k, v.data.shape) for k, v in net.blobs.items()]

### Layer parameteres and their shapes
[(k, v[0].data.shape) for k, v in net.params.items()]

# take an array of shape (n, height, width) or (n, height, width, channels)
# and visualize each (height, width) thing in a grid of size approx. sqrt(n) by sqrt(n)
def vis_square(data, padsize=1, padval=0):
    data -= data.min()
    data /= data.max()
    
    # force the number of filters to be square
    n = int(np.ceil(np.sqrt(data.shape[0])))
    padding = ((0, n ** 2 - data.shape[0]), (0, padsize), (0, padsize)) + ((0, 0),) * (data.ndim - 3)
    data = np.pad(data, padding, mode='constant', constant_values=(padval, padval))
    
    # tile the filters into an image
    data = data.reshape((n, n) + data.shape[1:]).transpose((0, 2, 1, 3) + tuple(range(4, data.ndim + 1)))
    data = data.reshape((n * data.shape[1], n * data.shape[3]) + data.shape[4:])
    
    plt.imshow(data)
    plt.show()

## First layer filters, conv1
# the parameters are a list of [weights, biases]
filters = net.params['conv1'][0].data
vis_square(filters.transpose(0, 2, 3, 1))

# The first layer output, conv1 (rectified responses of the filters above, first 36 only)
feat = net.blobs['conv1'].data[0, :36]
vis_square(feat, padval=1)

# The first layer output, conv1 (rectified responses of the filters above, first 36 only)
feat = net.blobs['conv1'].data[0, :36]
vis_square(feat, padval=1)

# The second layer filters, conv2 (256 filters, each of which has dimension 5*5*48)
filters = net.params['conv2'][0].data
vis_square(filters[:48].reshape(48**2, 5, 5))

# The second layer output, conv2 (rectified, only the first 36 of 256 channels)
feat = net.blobs['conv2'].data[0, :36]
vis_square(feat, padval=1)

# The third layer output, conv3 (rectified, all 384 channels)
feat = net.blobs['conv3'].data[0]
vis_square(feat, padval=0.5)

# The fourth layer output, conv4 (rectified, all 384 channels)
feat = net.blobs['conv4'].data[0]
vis_square(feat, padval=0.5)

# The fifth layer output, conv5 (rectified, all 256 channels)
feat = net.blobs['conv5'].data[0]
vis_square(feat, padval=0.5)

# The fifth layer after pooling, pool5
feat = net.blobs['pool5'].data[0]
vis_square(feat, padval=1)

# The first fully connected layer, fc6 (rectified)
feat = net.blobs['fc6'].data[0]
plt.subplot(2, 1, 1)
plt.plot(feat.flat)
plt.subplot(2, 1, 2)
_ = plt.hist(feat.flat[feat.flat > 0], bins=100)
plt.show()

# The second fully connected layer, fc7 (rectified)
feat = net.blobs['fc7'].data[0]
plt.subplot(2, 1, 1)
plt.plot(feat.flat)
plt.subplot(2, 1, 2)
_ = plt.hist(feat.flat[feat.flat > 0], bins=100)
plt.show()

# The final probability output, prob
feat = net.blobs['prob'].data[0]
plt.plot(feat.flat)
plt.show()

# Let's see the top 5 predicted labels.
# load labels
imagenet_labels_filename = caffe_root + 'data/DATASET/synsets.txt'
try:
    labels = np.loadtxt(imagenet_labels_filename, str, delimiter='\t')
except:
    print "Labels not found. (line 159)"

# sort top k predictions from softmax output
top_k = net.blobs['prob'].data[0].flatten().argsort()[-1:-6:-1]
print labels[top_k]

output_prob = net.blobs['prob'].data[0]
print output_prob[top_k]
