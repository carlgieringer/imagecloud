import argparse
import warnings

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from scipy.ndimage import gaussian_gradient_magnitude
from wordcloud import WordCloud, ImageColorGenerator

warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser(description="Generate a word cloud")
parser.add_argument("--text-path", required=True, help="path to a file containing text")
parser.add_argument("--image-path", required=True, help="path to a file containing an image")
parser.add_argument("--output-path", default="output/imagecloud.png", help="path to a output the word cloud image")
parser.add_argument("--downsample", type=int, default=1, help="amount by which to divide input image's pixels")
parser.add_argument("--seed", type=int, default=42, help="randomness seed")


def do_wordcloud(
        text_path,
        image_path,
        output_path="output/imagecloud.png",
        downsample_ratio=1,
        random_seed=42,
):
    """
    
    :param text_path: path to file containing text
    :param image_path: path to file containing image for masking and coloring
    :param output_path: where to output the WordCloud as an image
    :param downsample_ratio: divide image pixels by this
    :param random_state: the randomness seed for the WordCloud
    """
    
    # load wikipedia text on rainbow
    text = open(text_path).read()
    
    # load image. This has been modified in gimp to be brighter and have more saturation.
    image_data = np.array(Image.open(image_path))
    if len(image_data.shape) < 3:
        raise Exception("image_data needs three dimensions.  Is it a color image?")
    # subsample by factor of 3. Very lossy but for a wordcloud we don't really care.
    if downsample_ratio != 1:
        image_data = image_data[::downsample_ratio, ::downsample_ratio]
    
    # create mask  white is "masked out"
    mask = image_data.copy()
    mask[mask.sum(axis=2) == 0] = 255
    
    # some finesse: we enforce boundaries between colors so they get less washed out.
    # For that we do some edge detection in the image
    edges = np.mean([gaussian_gradient_magnitude(image_data[:, :, i] / 255., 2) for i in range(3)], axis=0)
    mask[edges > .08] = 255
    
    # create wordcloud. A bit sluggish, you can subsample more strongly for quicker rendering
    # relative_scaling=0 means the frequencies in the data are reflected less
    # acurately but it makes a better picture
    wc = WordCloud(
        max_words=2000,
        mask=mask,
        # max_font_size=40,
        random_state=random_seed,
        relative_scaling=0,
        mode="RGBA",
        # https://github.com/amueller/word_cloud/blob/master/wordcloud/stopwords
        # stopwords=,
    )
    
    # generate word cloud
    wc.generate(text)
    plt.title("Masked")
    plt.imshow(wc)
    
    # create coloring from image
    image_colors = ImageColorGenerator(image_data)
    wc.recolor(color_func=image_colors)
    plt.figure(figsize=(10, 10))
    plt.title("Recolored")
    plt.imshow(wc, interpolation="bilinear")
    wc.to_file(output_path)
    
    plt.figure(figsize=(10, 10))
    plt.title("Original Image")
    plt.imshow(image_data)
    
    plt.figure(figsize=(10, 10))
    plt.title("Edge map")
    plt.imshow(edges)
    plt.show()


if __name__ == "__main__":
    args = parser.parse_args()
    do_wordcloud(args.text_path, args.image_path, args.output_path, args.downsample, args.seed)
