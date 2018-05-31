import os
import numpy as np

data_save_base_dir = r'C:\Users\Administrator\Desktop\testData'
test_ids = [3]

def read_npz(data_save_base_dir, single_image_id):
    npz_name = os.path.join(data_save_base_dir + '\seg_npzs', str(single_image_id) + '_datas.npz')
    npz = np.load(npz_name)
    ins_boxes = npz['boxes']
    ins_labels = npz['labels']  # contains some class out of the 16 classes
    return ins_boxes, ins_labels

for i in test_ids:
    single_image_id = i
    foo(data_save_base_dir, single_image_id)
