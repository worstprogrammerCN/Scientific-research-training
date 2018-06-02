# -*- coding: utf-8 -*-
import png_to_text_mat
import argparse
import os
import numpy as np
import glob

parser = argparse.ArgumentParser()
args = parser.parse_args()

data_save_base_dir = r'testData2'


def get_all_test_data():
    files = glob.glob(data_save_base_dir + '\seg_npzs\*.npz')
    test_ids = [int(file.split("\\")[-1].split('_')[-2]) for file in files]
    return test_ids


def read_npz(data_save_base_dir, single_image_id):
    npz_name = os.path.join(data_save_base_dir + '\seg_npzs', str(single_image_id) + '_datas.npz')
    npz = np.load(npz_name)
    ins_boxes = npz['boxes']
    ins_labels = npz['labels']  # contains some class out of the 16 classes
    return ins_boxes, ins_labels

def main():
    test_ids = get_all_test_data()
    for i in test_ids:
        print("----------number %d----------" % i)
        pred_boxes, pred_class_ids = read_npz(data_save_base_dir, i)
        caption, index_list, indexes = png_to_text_mat.png2text(pred_boxes, pred_class_ids)
        print("文字描述:", caption)
        print("index_list", index_list)
        print("indexes", indexes)

if __name__ == '__main__':
    main()
