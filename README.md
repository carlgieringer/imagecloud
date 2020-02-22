# imagecloud

Makes a word cloud based upon an image.

# Usage

You must provide the text and the image.  Google image search lets you filter by size (large), color (transparent),
and usage rights (labeled for reuse).

```
# requires Python 3
pip install -r requirements.txt

# show help
python imagecloud.py --help

# Get some data
mkdir data
curl https://upload.wikimedia.org/wikipedia/commons/2/22/Earth_Western_Hemisphere_transparent_background.png > data/earthwiki.png
curl https://www.ipcc.ch/site/assets/uploads/2018/02/SYR_AR5_FINAL_full.pdf > data/ipcc_ar5.pdf
# one way to get pdftotext is with `brew install poppler` 
pdftotext data/ipcc_ar5.pdf data/ipcc_ar5.txt
 
python imagecloud.py --text-path data/ipcc_ar5.txt --image-path data/earthwiki.png --output-path output/earthcloud.png \
  --max-words 2000 --relative-scaling 0.7
```
