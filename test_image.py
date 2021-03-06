from sklearn.externals import joblib
import argparse
import cv2
from utils import *
from matplotlib import pyplot as plt
import time

desp_dim = 11
normalize_value = 255
sub_window = 32


def main(test_image):
    # decide whether a model exist
    save_addr = './save_model'
    model_dir = ''
    model_exist = False
    model_list = getFileListFromDir(save_addr, filetype='pkl')
    if cv2.__version__[0] == '3':
        prefix = 'cv3'
    else:
        prefix = 'cv2'
    for filename in model_list:
        if prefix in filename:
            print "kmeans model exists"
            model_exist = True
            model_addr = filename
    print "Kmeans model addr : " + model_addr
    if model_exist:
        kmeans = joblib.load(model_addr)  # load pre-trained k-means model #
        # print ('kmeans parameters', kmeans.get_params())
    else:
        print "please generate kmeans model for pixel"
        sys.exit(0)

    # get k-means init value
    init_value = kmeans.get_params()['init']

    # train histogram
    test_dir = "./image_jpg/"
    desp_save_dir = "./descriptor/"
    hist_dir = "./hist/"
    image_list = getFileListFromDir(test_dir, filetype='npy')
    hist_list = getFileListFromDir(hist_dir, filetype='npy')
    hist_num = len(hist_list)
    hist_total = []

    # test_image = "nessne04"
    test_addr = test_dir + test_image + ".jpg"
    print "teating image : ", test_addr
    test_image = test_addr.split('/')[-1].split('.')[0]
    desp_list = getFileListFromDir(desp_save_dir, filetype='npy')
    desp_exist = False
    for despfile in desp_list:
        if test_image in despfile:
            desp_exist = True

    if desp_exist:
        print "reading exist descriptor file"
        des = np.load(desp_save_dir + test_image + "_dsp.npy")
    else:
        print "creating descriptor"
        img = cv2.imread(test_addr)
        img_lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        des = descriptor_generator(img_lab)

    lines = des.shape[0] * des.shape[1]
    des_reshape = np.reshape(des, (lines, desp_dim))
    label = kmeans.predict(des_reshape)
    label_reshape = np.reshape(label, (des.shape[0], des.shape[1]))
    label_pixel = label_reshape * 15
    # plt.imshow(label_reshape.astype(np.uint8),cmap ="gray")
    # plt.show()

    # get 12 layer image
    layer_num = kmeans.get_params()['n_clusters']
    layers = np.zeros((label_reshape.shape[0], label_reshape.shape[1], layer_num))
    for layer in range(layer_num):
        tmp = label_reshape.copy()
        tmp[tmp == layer] = normalize_value
        tmp[tmp != 255] = 0
        '''plt.imshow(tmp.astype(np.uint8),cmap ="gray")
        plt.show()  
        plt.close()'''
        integral = generate_integral_image(tmp, normalize_value)
        '''plt.imshow(integral, cmap ="gray")
        plt.show()
        plt.close()'''
        layers[:, :, layer] = integral[0:-1, 0:-1].copy()

    # generate histogram
    hist_addr = hist_dir + test_image
    hist = generate_histogram(layers, sub_window)

    # debug
    '''hist_reshape = np.reshape(hist, (label_reshape.shape[0], label_reshape.shape[1],12))
    hist_pixel = np.zeros(label_reshape.shape)
    for i in range(label_reshape.shape[0]):
        for j in range(label_reshape.shape[1]):
            for k in range(12):
                if hist_reshape[i,j,k] == np.max(hist_reshape[i,j,:]):
                    hist_pixel[i,j] = k
    plt.imshow(hist_pixel,cmap ="gray")
    plt.show()
    plt.close()'''

    # read kmeans hist
    save_addr = './save_hist_model'
    model_dir = ''
    model_exist = False
    model_list = getFileListFromDir(save_addr, filetype='pkl')
    if cv2.__version__[0] == '3':
        prefix = 'cv3'
    else:
        prefix = 'cv2'
    for filename in model_list:
        if prefix in filename:
            print "kmeans model exists"
            model_exist = True
            model_addr = filename
    print "Kmeans model addr : " + model_addr
    if model_exist:
        kmeans_hist = joblib.load(model_addr)  # load pre-trained k-means model
        # print ('kmeans parameters', kmeans.get_params())
    else:
        print "please generate kmeans model for hist"
        sys.exit(0)

    # predict hist for test image
    label_hist = kmeans_hist.predict(hist)
    original = cv2.imread(test_dir + test_image + ".jpg")[1:-1, 1:-1, :]
    original = cv2.cvtColor(original,cv2.COLOR_BGR2RGB)
    col_img = colorizeImage(original.shape,label_hist)

    #label_hist_reshape = np.reshape(label_hist, label_reshape.shape)

    #show images
    plt.figure(1)
    plt.imshow(original)
    plt.figure(2)
    plt.imshow(col_img)
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", type=str, default="helston4",
                        help="training set addr")
    args = parser.parse_args()
    img_addr = args.i
    print "img_addr : %s" % (img_addr)
    main(img_addr)
