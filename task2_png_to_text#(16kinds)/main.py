# -*- coding: utf-8 -*-
import png_to_text_mat
from operator import itemgetter, attrgetter
from bottle import template
import webbrowser
import argparse
import os
import scipy.io
parser = argparse.ArgumentParser()
#parser.add_argument("--mat_dir", type=str, default="../val/level0/", help="Mat Directory")#path of mat
#parser.add_argument("--out_dir", type=str, default="../val/level1/", help="Json Directory")#path of sort_mat output
# parser.add_argument("--image_dir", type=str, default="../val/DRAWING_GT/", help="Image Directory")#path of image
# parser.add_argument("--caption_dir", type=str, default="caption.txt", help="Caption Directory")#path of save caption for user
# parser.add_argument("--text_dir", type=str, default="text.txt", help="Text Directory")#path of save text for training
args = parser.parse_args()

def main():
    #pred_boxes=[[100,400,300,600],[50,300,150,400],[10,10,30,30],[100,500,300,700]]
    #pred_class_ids=[14,32,41,14]
    pred_boxes =[[50, 593, 140, 767, ], [79, 93, 171, 222, ], [692, 185, 762, 300, ], [643, 483, 698, 585, ],
     [357, 449, 551, 563, ], [642, 4, 705, 66, ], [389, 0, 655, 379, ], [439, 354, 460, 419, ], [387, 642, 536, 754, ],
     [0, 0, 111, 103, ], [220, 611, 393, 746, ], [359, 574, 469, 636, ], [267, 0, 379, 80, ], [666, 559, 716, 604, ],
     [186, 235, 398, 579, ], [677, 347, 715, 399, ], [253, 727, 394, 767, ], [257, 54, 378, 212, ],
     [669, 42, 718, 94, ]]
    pred_class_ids =[18, 18, 27, 27, 32, 27, 12, 27, 32, 18, 43, 32, 43, 25, 29, 25, 43, 43, 25]

    #get caption for user
    #caption,items=png_to_text_mat.png2text(class_gt_mat,instance_gt_mat)
    caption,index= png_to_text_mat.png2text(pred_boxes, pred_class_ids)
    #get text for training
    #txt,bg_text=trans.trans(caption)

    print (caption)
    print (index)

if __name__ == '__main__':
    main()

