#!/usr/bin/env python
import time
import sys

from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image

# Add image file location in rpi
image_file = "./expression.gif"

gif = Image.open(image_file)

try:
    num_frames = gif.n_frames
except Exception:
    sys.exit("provided image is not a gif")


# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.gpio_slowdown = 4
options.chain_length = 2
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'  # If you have an Adafruit HAT: 'adafruit-hat'
# options.daemon = 1; # Run as background process

matrix = RGBMatrix(options = options)

# Preprocess the gifs frames into canvases to improve playback performance
frames = []
canvas = matrix.CreateFrameCanvas()
print("Preprocessing gif, this may take a moment depending on the size of the gif...")
for frame_index in range(0, num_frames):
    gif.seek(frame_index)
    frame = gif.copy()
    # must copy the frame out of the gif, since thumbnail() modifies the image in-place
    combined = Image.new(frame.mode, (128, 32))
    combined.paste(frame, (0,0))
    combined.paste(frame.transpose(Image.FLIP_LEFT_RIGHT), (64, 0))
    combined.thumbnail((128, 32), Image.Resampling.LANCZOS)
    frames.append(combined.convert("RGB"))

# Close the gif file to save memory now that we have copied out all of the frames
gif.close()

print("Completed Preprocessing, displaying gif")

try:
    print("Press CTRL-C to stop.")

    # Infinitely loop through the gif
    cur_frame = 0
    while(True):
        canvas.SetImage(frames[cur_frame])
        matrix.SwapOnVSync(canvas, framerate_fraction=10)
        if cur_frame == num_frames - 1:
            cur_frame = 0
        else:
            cur_frame += 1
except KeyboardInterrupt:
    sys.exit(0)
