import io
import time
from concurrent import futures

import grpc
import numpy as np
import tensorflow as tf
from PIL import Image

import serving_pb2
import serving_pb2_grpc
from detector import CLASS_NAMES, Detector
from utils import bitmask_to_image, load_bytes_image_array, roi_to_rect

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class ObjectDetection(serving_pb2_grpc.ObjectDetectionServicer):

    def __init__(self, mask_format='png'):
        self._graph = tf.get_default_graph()
        self._detector = Detector('mask_rcnn_coco.h5')
        self._mask_format = mask_format

    def Detect(self, request, context):
        img = load_bytes_image_array(request.image)

        with self._graph.as_default():
            r = self._detector.detect(img)

        class_ids = r['class_ids']
        rois = r['rois']
        masks_t = np.transpose(r['masks'], axes=(2, 0, 1))

        for class_id, roi, mask in zip(class_ids, rois, masks_t):
            img = bitmask_to_image(mask)

            buffer = io.BytesIO()
            img.save(buffer, self._mask_format)

            x, y, width, height = roi_to_rect(roi)
            rect = serving_pb2.Rectangle(x=x, y=y, width=width, height=height)

            yield serving_pb2.Object(
                label=CLASS_NAMES[class_id],
                rect=rect,
                segmentation=buffer.getvalue())


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
