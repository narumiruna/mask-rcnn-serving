import argparse
import os
import tempfile

import numpy as np
from PIL import Image

from mrcnn import model as modellib
from mrcnn import utils
from mrcnn.config import Config
from utils import load_image_array

CLASS_NAMES = [
    'BG', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train',
    'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign',
    'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
    'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag',
    'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite',
    'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
    'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon',
    'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot',
    'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant',
    'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
    'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
    'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear',
    'hair drier', 'toothbrush'
]


class InferenceConfig(Config):
    NAME = "coco"
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1
    NUM_CLASSES = 1 + 80


class Detector(object):

    def __init__(self, model_path, verbose=1):
        self._model_path = model_path
        self._verbose = verbose

        if not os.path.exists(self._model_path):
            utils.download_trained_weights(self._model_path)

        config = InferenceConfig()
        self._model = modellib.MaskRCNN('inference', config,
                                        tempfile.TemporaryDirectory().name)
        self._model.load_weights(self._model_path, by_name=True)

    def detect(self, img):
        return self._model.detect([img], verbose=self._verbose)[0]


def test():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='mask_rcnn_coco.h5')
    parser.add_argument('--image', type=str, default='example.jpg')
    args = parser.parse_args()

    detector = Detector(args.model)
    image = load_image_array(args.image)
    r = detector.detect(image)

    for i, (roi, class_id) in enumerate(zip(r['rois'], r['class_ids'])):
        print('Object #{}, roi: {}, class: {}'.format(i + 1, roi,
                                                      CLASS_NAMES[class_id]))


if __name__ == '__main__':
    test()
