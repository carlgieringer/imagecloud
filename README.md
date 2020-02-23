# imagecloud

Makes a word cloud based upon an image.

![globe-shaped word cloud of climate change text](output/example-earthcloud.png?raw=true)

This started as just a thin wrapper around [word_cloud](https://github.com/amueller/word_cloud) (based upon 
parameterizing the [parrot example](https://github.com/amueller/word_cloud/blob/master/examples/parrot.py).)  It now
additionally includes configurable edge detection (`--edge-strategy`) and removal of small edge artifacts
(`--small-object-size`).

## Quick start

You must provide the text and the image.  Google image search lets you filter by size (e.g., "large"), color (e.g., 
"transparent"), and usage rights (e.g., "labeled for reuse").

```
# requires Python 3
pip install -r requirements.txt

# show help
python imagecloud.py --help

# get some data
mkdir data
curl https://storage.needpix.com/rsynced_images/world-1301744_1280.png > data/earth.png
curl https://www.ipcc.ch/site/assets/uploads/2018/02/SYR_AR5_FINAL_full.pdf > data/ipcc_ar5.pdf
# one way to get pdftotext is with `brew install poppler` 
pdftotext data/ipcc_ar5.pdf data/climate.txt

# make a word cloud
python imagecloud.py --text-path data/climate.txt --image-path data/earth.png --output-path output/earthcloud.png \
  --max-words 2000 --relative-scaling 0 --seed 42 --log-level DEBUG --edge-sigma 7
```

# Full usage

```
python imagecloud.py --help
usage: imagecloud.py [-h] --text-path TEXT_PATH --image-path IMAGE_PATH [--output-path OUTPUT_PATH] [--downsample DOWNSAMPLE] [--seed SEED] [--no-detect-edges] [--edge-sigma EDGE_SIGMA] [--edge-threshold EDGE_THRESHOLD]
                     [--extra-stopwords EXTRA_STOPWORDS] [--max-font-size MAX_FONT_SIZE] [--max-words MAX_WORDS] [--relative-scaling RELATIVE_SCALING] [--no-plot] [--log-level LOG_LEVEL] [--edge-strategy {gaussian,canny}]
                     [--small-object-size SMALL_OBJECT_SIZE]

Generate a word cloud

optional arguments:
  -h, --help            show this help message and exit
  --text-path TEXT_PATH
                        path to a file containing text
  --image-path IMAGE_PATH
                        path to a file containing an image
  --output-path OUTPUT_PATH
                        path to a output the word cloud image
  --downsample DOWNSAMPLE
                        amount by which to divide input image's pixels
  --seed SEED           randomness seed
  --no-detect-edges     skip edge detection
  --edge-sigma EDGE_SIGMA
                        standard deviations of the Gaussian filter used for edge detection
  --edge-threshold EDGE_THRESHOLD
                        cutoff of gaussian filter above which edge is detected
  --extra-stopwords EXTRA_STOPWORDS
                        comma-separated list of stopwords to add to default
  --max-font-size MAX_FONT_SIZE
                        maximum font size of a word in the cloud
  --max-words MAX_WORDS
                        maximum number of words in cloud
  --relative-scaling RELATIVE_SCALING
                        relative importance of frequency vs. rank for word size. 0 is completely rank. 1 iscompletely frequency.
  --no-plot             skip plotting
  --log-level LOG_LEVEL
                        log level (DEBUG, INFO, WARNING, or ERROR)
  --edge-strategy {gaussian,canny}
                        how to detect edges
  --small-object-size SMALL_OBJECT_SIZE
                        size in pixels of small objects to remove from edge detection
```

