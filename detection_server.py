import io
import time
from concurrent import futures

import logging
import cv2
import grpc
import numpy as np
import tensorflow as tf
from PIL import Image

import serving_pb2
import serving_pb2_grpc
import utils
from detector import CLASS_NAMES, Detector

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class ObjectDetection(serving_pb2_grpc.ObjectDetectionServicer):

    def __init__(self, model_path='mask_rcnn_coco.h5', mask_format='png'):
        self._graph = tf.get_default_graph()
        self._detector = Detector(model_path)
        self._mask_format = mask_format

    def Detect(self, request, context):
        img = utils.load_bytes_image_array(request.image)

        objects = []

        with self._graph.as_default():
            r = self._detector.detect(img)

        class_ids = r['class_ids']
        rois = r['rois']
        masks_t = np.transpose(r['masks'], axes=(2, 0, 1))

        for class_id, roi, mask in zip(class_ids, rois, masks_t):
            sequence = utils.mask_to_polygon(mask)
            if sequence is None:
                continue

            x, y, width, height = utils.roi_to_rect(roi)
            box = serving_pb2.Rectangle(x=x, y=y, width=width, height=height)
            shape = serving_pb2.Shape(
                contentType='polygon/series', series=sequence)
            objects.append(serving_pb2.Object(label=CLASS_NAMES[class_id], box=box, shape=shape))
        return serving_pb2.DetectionResponse(type="objects", objects=objects)

    def DetectStream(self, request, context):
        img = utils.load_bytes_image_array(request.image)

        with self._graph.as_default():
            r = self._detector.detect(img)

        class_ids = r['class_ids']
        rois = r['rois']
        masks_t = np.transpose(r['masks'], axes=(2, 0, 1))

        for class_id, roi, mask in zip(class_ids, rois, masks_t):
            sequence = utils.mask_to_polygon(mask)
            if sequence is None:
                continue

            x, y, width, height = utils.roi_to_rect(roi)
            box = serving_pb2.Rectangle(x=x, y=y, width=width, height=height)
            shape = serving_pb2.Shape(
                contentType='polygon/series', series=sequence)
            yield serving_pb2.Object(
                label=CLASS_NAMES[class_id], box=box, shape=shape)


def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    serving_pb2_grpc.add_ObjectDetectionServicer_to_server(
        ObjectDetection(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    main()
