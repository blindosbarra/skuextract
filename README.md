# skuextract
Extract sku 

create an API KEY from the google console, restrict the key to Cloud Billing API

Clone the repo, install the python dependencies with:

pip3 install -r requirements.txt

run the script:

python3 extractor.py --key KEY_NUMBER

wait some minutes and you will find the skus as csvs

services_skus.csv
skus_list.csv


you can edit the variables in the script to add or remove regions and other filters
