import argparse
import os
import tempfile

import numpy as np
import tensorflow as tf

from mrcnn import model as modellib
from mrcnn import utils
from mrcnn.config import Config

from .utils import load_image_array, load_config

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


class MaskRCNNObject(object):

    def __init__(self, roi, class_id, score, mask):
        self.roi = roi
        self.class_id = class_id
        self.score = score
        self.mask = mask

    @property
    def label(self):
        return CLASS_NAMES[self.class_id]

    @property
    def name(self):
        return self.__class__.__name__

    def __repr__(self):
        return '{}, roi: {}, label: {}.'.format(self.name, self.roi, self.label)


class Detector(object):

    def __call__(self, image):
        return self.detect(image)

    def detect(self, image):
        raise NotImplementedError


class MaskRCNNDetector(Detector):

    def __init__(self, model_path, model_config, verbose=1):
        self._model_path = model_path
        self._model_config = model_config
        self._verbose = verbose
        self._graph = tf.get_default_graph()

        if not os.path.exists(self._model_path):
            utils.download_trained_weights(self._model_path)

        self._model = modellib.MaskRCNN('inference', model_config,
                                        tempfile.TemporaryDirectory().name)
        self._model.load_weights(self._model_path, by_name=True)

    def detect(self, image):
        """
        Args:
            image(ndarray): image to detect

        Returns a list of MaskRCNNDetectedObject
        """
        with self._graph.as_default():
            r = self._model.detect([image], verbose=self._verbose)[0]

        rois = r['rois']
        class_ids = r['class_ids']
        scores = r['scores']
        masks = np.transpose(r['masks'], axes=(2, 0, 1))

        detected_objects = []
        for roi, class_id, score, mask in zip(rois, class_ids, scores, masks):
            obj = MaskRCNNObject(roi, class_id, score, mask)
            detected_objects.append(obj)

        return detected_objects


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--model-path',
        type=str,
        default='mask_rcnn_coco.h5',
        help='path of model file')
    parser.add_argument(
        '--model-config',
        type=str,
        default='config/inference.yaml',
        help='path of inference config')
    parser.add_argument(
        '--image-path',
        type=str,
        default='example.jpg',
        help='path of image file')
    args = parser.parse_args()

    model_config = load_config(args.model_config)

    detector = MaskRCNNDetector(args.model_path, model_config)
    image = load_image_array(args.image_path)
    detected_objects = detector(image)

    for detected_object in detected_objects:
        print(detected_object)


if __name__ == '__main__':
    main()
