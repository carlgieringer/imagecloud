import argparse
import logging
import os
import warnings
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from scipy.ndimage import gaussian_gradient_magnitude
from skimage import feature, morphology
from wordcloud import WordCloud, ImageColorGenerator, STOPWORDS

warnings.filterwarnings("ignore")
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.WARNING,
    datefmt='%Y-%m-%d %H:%M:%S'
)
_logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description="Generate a word cloud")
parser.add_argument("--text-path", required=True, help="path to a file containing text")
parser.add_argument("--image-path", required=True, help="path to a file containing an image")
parser.add_argument("--output-path", default="output/imagecloud.png", help="path to a output the word cloud image")
parser.add_argument("--downsample", type=int, default=1, help="amount by which to divide input image's pixels")
parser.add_argument("--seed", type=int, default=None, help="randomness seed")
parser.add_argument("--no-detect-edges", action='store_true', default=False, help="skip edge detection")
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
parser.add_argument("--no-plot", action="store_true", default=False, help="skip plotting")
parser.add_argument("--log-level", default=logging.INFO, help="log level (DEBUG, INFO, WARNING, or ERROR)")
parser.add_argument("--edge-strategy", choices=("gaussian", "canny"), default="canny", help="how to detect edges")
parser.add_argument("--small-object-size", type=int, default=None, help="size in pixels of small objects to remove from"
                                                                        " edge detection")

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
        do_plot=True,
        edge_strategy="canny",
        small_object_size=None,
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
    :param do_plot: whether to show informative plots in addition to saving image
    :param edge_strategy: how to detect edges: gaussian or canny
    :param small_object_size: the size in pixels of small objects to remove from edge detection.
    """

    text = open(text_path).read()

    image = Image.open(image_path)
    image_data = np.array(image)
    if len(image_data.shape) < 3:
        raise Exception("image_data needs three dimensions. (did you provice a color image?)")
    if downsample_ratio != 1:
        _logger.debug("downsampling by %d", downsample_ratio)
        image_data = image_data[::downsample_ratio, ::downsample_ratio]

    # create mask  white is "masked out"
    mask = image_data.copy()
    mask[mask.sum(axis=2) == _ALPHA_TRANSPARENT] = _MASK_EXCLUDE

    edges = None
    if do_detect_edges:
        _logger.debug("calculating edges")
        if edge_strategy == "gaussian":
            edges = np.mean([gaussian_gradient_magnitude(image_data[:, :, i] / 255., edge_sigma) for i in range(3)], axis=0)
        elif edge_strategy == "canny":
            edges = np.mean([feature.canny(image_data[:, :, i] / 255., sigma=edge_sigma) for i in range(3)], axis=0)
            if small_object_size:
                _logger.debug("removing objects smaller than %d pixels", small_object_size)
                without_objects = morphology.remove_small_objects(edges > edge_threshold, small_object_size)
                edges = without_objects.astype(int) * edges
        _logger.debug("calculated edges")

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

    _logger.debug("generating word cloud")
    wc.generate(text)
    _logger.debug("generated word cloud")

    if do_plot:
        plt.title("WordCloud")
        _logger.debug("plotting WordCloud")
        plt.imshow(wc)

    # create coloring from image
    image_colors = ImageColorGenerator(image_data)
    wc.recolor(color_func=image_colors)

    output_dir = os.path.dirname(output_path)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    _logger.debug("writing file")
    wc.to_file(output_path)

    if do_plot:
        plt.figure(figsize=(10, 10))
        plt.title("WordCloud Recolored")
        _logger.debug("plotting WordCloud Recolored")
        plt.imshow(wc, interpolation="bilinear")

        plt.figure(figsize=(10, 10))
        plt.title("Original Image")
        _logger.debug("plotting Original Image")
        plt.imshow(image_data)

        plt.figure(figsize=(10, 10))
        plt.title("Mask")
        _logger.debug("plotting Mask")
        plt.imshow(mask)

        if edges is not None:
            plt.figure(figsize=(10, 10))
            plt.title("Edges")
            _logger.debug("plotting Edges")
            plt.imshow(edges)

        _logger.debug("showing plot")
        plt.show()


if __name__ == "__main__":
    args = parser.parse_args()

    _logger.setLevel(logging.getLevelName(args.log_level))

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
        do_plot=not args.no_plot,
        edge_strategy=args.edge_strategy,
        small_object_size=args.small_object_size,
    )
