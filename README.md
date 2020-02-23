# imagecloud

Makes a word cloud based upon an image.

![globe-shaped word cloud of climate change text](output/example-earthcloud.png?raw=true)

# Usage

You must provide the text and the image.  Google image search lets you filter by size (large), color (transparent),
and usage rights (labeled for reuse).

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
