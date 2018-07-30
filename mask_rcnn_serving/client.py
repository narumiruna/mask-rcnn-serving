import argparse

import grpc
from PIL import Image, ImageDraw

from . import serving_pb2, serving_pb2_grpc, utils


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='0.0.0.0')
    parser.add_argument('--port', type=str, default='50051')
    parser.add_argument(
        '--image-path',
        type=str,
        default='example.jpg',
        help='path of image file')
    args = parser.parse_args()
    print(args)

    with open(args.image_path, 'rb') as f:
        img = f.read()

    address = '{}:{}'.format(args.host, args.port)
    channel = grpc.insecure_channel(address)
    stub = serving_pb2_grpc.ObjectDetectionStub(channel)
    objects = stub.DetectStream(serving_pb2.DetectionRequest(image=img))

    img = Image.open(args.image_path).convert('RGB')

    for i, obj in enumerate(objects):
        # print object info
        utils.print_object(obj, index=i + 1)

        draw = ImageDraw.Draw(img)
        # draw bounding box
        if obj.box:
            draw.rectangle(utils.rect_to_roi(obj.box), outline='blue')

        # draw polygon
        if obj.shape:
            draw.polygon(xy=obj.shape.series, outline='red')

    img.show()


if __name__ == '__main__':
    main()
