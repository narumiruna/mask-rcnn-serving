import argparse
import time
from concurrent import futures

import grpc

from . import serving_pb2, serving_pb2_grpc, utils
from .detector import MaskRCNNDetector
from .utils import load_config

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


def mrcnn_object_to_grpc_object(detected_object):
    mask = detected_object.mask
    sequence = utils.mask_to_polygon(mask)
    if sequence is None:
        return None

    x, y, width, height = utils.roi_to_rect(detected_object.roi)

    box = serving_pb2.Rectangle(x=x, y=y, width=width, height=height)
    shape = serving_pb2.Shape(contentType='polygon/series', series=sequence)

    grpc_object = serving_pb2.Object(
        label=detected_object.label, box=box, shape=shape)

    return grpc_object


def mrcnn_objects_to_grpc_objects(detected_objects):
    grpc_objects = []

    for detected_object in detected_objects:
        if detected_object is None:
            continue
        grpc_objects.append(detected_object)

    return grpc_objects


class ObjectDetection(serving_pb2_grpc.ObjectDetectionServicer):

    def __init__(self, detector):
        self._detector = detector

    def Detect(self, request, context):
        image = utils.load_bytes_image_array(request.image)

        mrcnn_objects = self._detector(image)

        grpc_objects = mrcnn_objects_to_grpc_objects(mrcnn_objects)

        return serving_pb2.DetectionResponse(
            type="objects", objects=grpc_objects)

    def DetectStream(self, request, context):
        image = utils.load_bytes_image_array(request.image)

        mrcnn_objects = self._detector(image)

        for mrcnn_object in mrcnn_objects:
            grpc_object = mrcnn_object_to_grpc_object(mrcnn_object)

            if grpc_object is None:
                continue

            yield grpc_object


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='0.0.0.0')
    parser.add_argument('--port', type=str, default='50051')
    parser.add_argument(
        '--model-path',
        type=str,
        default='mask_rcnn_coco.h5',
        help='path of model file')
    parser.add_argument(
        '--model-config',
        type=str,
        default='config/inference.yaml',
        help='path of inference config file')
    parser.add_argument('--max-workers', type=int, default=10)
    args = parser.parse_args()

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=args.max_workers))

    model_config = load_config(args.model_config)
    detector = MaskRCNNDetector(args.model_path, model_config)

    serving_pb2_grpc.add_ObjectDetectionServicer_to_server(
        ObjectDetection(detector=detector), server)

    address = '{}:{}'.format(args.host, args.port)
    server.add_insecure_port(address)
    server.start()
    print("Listening at {}".format(address))
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    main()
