import argparse
import os
import warnings
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from scipy.ndimage import gaussian_gradient_magnitude
from wordcloud import WordCloud, ImageColorGenerator, STOPWORDS

warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser(description="Generate a word cloud")
parser.add_argument("--text-path", required=True, help="path to a file containing text")
parser.add_argument("--image-path", required=True, help="path to a file containing an image")
parser.add_argument("--output-path", default="output/imagecloud.png", help="path to a output the word cloud image")
parser.add_argument("--downsample", type=int, default=1, help="amount by which to divide input image's pixels")
parser.add_argument("--seed", type=int, default=None, help="randomness seed")
parser.add_argument("--no-detect-edges", action='store_true', default=False, help="whether to skip edge detection")
parser.add_argument("--edge-sigma", type=float, default=2,
                    help="standard deviations of the Gaussian filter used for edge detection")
parser.add_argument("--edge-threshold", type=float, default=0.08,
                    help="cutoff of gaussian filter above which edge is detected")
parser.add_argument("--extra-stopwords", default=None, help="comma-separated list of stopwords to add to default")
parser.add_argument("--max-font-size", type=int, default=None, help="maximum font size of a word in the cloud")
parser.add_argument("--max-words", type=int, default=200, help="maximum number of words in cloud")
parser.add_argument("--relative-scaling", type=float, default=0.5,
                    help="relative importance of frequency vs. rank for word size.  0 is completely rank.  1 is"
                         "completely frequency.")


_ALPHA_TRANSPARENT = 0
_MASK_EXCLUDE = 255

def do_wordcloud(
        text_path,
        image_path,
        output_path="output/imagecloud.png",
        downsample_ratio=1,
        random_seed=None,
        do_detect_edges=True,
        edge_sigma=2,
        edge_threshold=0.8,
        extra_stopwords=None,
        max_font_size=None,
        max_words=200,
        relative_scaling=0.5,
):
    """
    :param text_path: path to file containing text
    :param image_path: path to file containing image for masking and coloring
    :param output_path: where to output the WordCloud as an image
    :param downsample_ratio: divide image pixels by this
    :param random_seed: the randomness seed for the WordCloud
    :param do_detect_edges: whether to do edge detection 
    :param edge_sigma: standard deviations of the Gaussian filter used for edge detection
    :param edge_threshold: threshold of Gaussian used for edge detection
    :param extra_stopwords: extra stopwords.  If missing, defaults are used.
    :param max_font_size: maximum font size of any word
    :param max_words: maximum number of words
    :param relative_scaling: relative importance of frequency vs. rank for word size.  0 is completely rank.  1 is
                             completely frequency.
    """
    
    text = open(text_path).read()
    
    image = Image.open(image_path)
    image_data = np.array(image)
    if len(image_data.shape) < 3:
        raise Exception("image_data needs three dimensions. (did you provice a color image?)")
    if downsample_ratio != 1:
        image_data = image_data[::downsample_ratio, ::downsample_ratio]
    
    # create mask  white is "masked out"
    mask = image_data.copy()
    mask[mask.sum(axis=2) == _ALPHA_TRANSPARENT] = _MASK_EXCLUDE
    
    edges = None
    if do_detect_edges:
        # some finesse: we enforce boundaries between colors so they get less washed out.
        # For that we do some edge detection in the image
        edges = np.mean([gaussian_gradient_magnitude(image_data[:, :, i] / 255., edge_sigma) for i in range(3)], axis=0)
        mask[edges > edge_threshold] = _MASK_EXCLUDE
    
    stopwords = STOPWORDS if extra_stopwords is None else STOPWORDS | set(extra_stopwords.split(","))
    
    wc = WordCloud(
        max_words=max_words,
        mask=mask,
        max_font_size=max_font_size,
        random_state=random_seed,
        # relative_scaling=0 means the frequencies in the data are reflected less
        # accurately but it makes a better picture
        relative_scaling=relative_scaling,
        mode="RGBA",
        stopwords=stopwords,
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

    output_dir = os.path.dirname(output_path)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    wc.to_file(output_path)
    
    plt.figure(figsize=(10, 10))
    plt.title("Original Image")
    plt.imshow(image_data)
    
    if edges is not None:
        plt.figure(figsize=(10, 10))
        plt.title("Edge map")
        plt.imshow(edges)
    
    plt.show()


if __name__ == "__main__":
    args = parser.parse_args()
    do_wordcloud(
        text_path=args.text_path,
        image_path=args.image_path,
        output_path=args.output_path,
        downsample_ratio=args.downsample,
        random_seed=args.seed,
        do_detect_edges=not args.no_detect_edges,
        edge_sigma=args.edge_sigma,
        edge_threshold=args.edge_threshold,
        extra_stopwords=args.extra_stopwords,
        max_font_size=args.max_font_size,
        max_words=args.max_words,
        relative_scaling=args.relative_scaling,
    )
