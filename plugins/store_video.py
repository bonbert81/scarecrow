import sys
sys.path.append('..')
from PIL import Image
import cv2
import numpy as np
from plugin_base.base import *
import datetime

class StoreVideoPlugin(ImageDetectorBasePlugin):
    def __init__(self, configuration):
        self.buffer = []
        self.fps = float(configuration['Video']['FPS'])
        self.video_path = configuration['Video']['Path']
        self.codec = configuration['Video']['Codec']
        self.name = configuration['Video']['OutName']
        try:
            self.buffer_size = int(configuration['Video']['BufferSize'])
        except Exception:
            target_len = int(configuration['Video']['TargetLengthSeconds'])
            self.buffer_size = target_len*self.fps
            print('Using TargetLengthSeconds, setting to {}'.format(self.buffer_size))
        ImageDetectorBasePlugin.__init__(self, configuration)

    def run_after(self, res, ix, confidence, np_det_img):
        # TODO: SIGTERM handler
        # TODO: detection labels as *args
        print(res, ix, confidence, )
        print('StoreVideoPlugin run_after ix {} / buf {}'.format(ix, len(self.buffer)))
        if np_det_img is not None:
            img = np_det_img.astype(np.uint8)
            self.buffer.append(img)
        else:
            print('Store video frame is null?')

        if len(self.buffer) > self.buffer_size:
            print('Flushing video')
            dt = datetime.datetime.now().isoformat()
            fourcc = cv2.VideoWriter_fourcc(*self.codec) #mp4v
            video = cv2.VideoWriter(
                '{}/{}_{}'.format(self.video_path, dt, self.name), 
                fourcc, 
                self.fps, 
                (self.buffer[0].shape[1], self.buffer[0].shape[0]),
                True)
            for frame in self.buffer:
                video.write(frame)
            video.release()
            cv2.destroyAllWindows()
            # Clear buffer
            self.buffer = []
            # Save a separate key frame 
            img = Image.fromarray(np_det_img, 'RGB')
            img.save('{}/{}_{}_thumb.jpg'.format(self.video_path, dt, ix))
