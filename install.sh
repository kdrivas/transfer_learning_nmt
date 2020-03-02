# Download data
mkdir -p data/transfer
wget --header="Host: doc-04-2o-docs.googleusercontent.com" --header="User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36" --header="Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9" --header="Accept-Language: es-ES,es;q=0.9" --header="Referer: https://drive.google.com/drive/u/1/folders/1_oizRFnDsAp75sutzLeNfkEqduwm2AwM" --header="Cookie: AUTH_0bl49mdmcbo80irb4rdjkgnre04gdie9_nonce=ii1p8hveidr38; _ga=GA1.2.1055865327.1554740011" --header="Connection: keep-alive" "https://doc-04-2o-docs.googleusercontent.com/docs/securesc/moh3ovbqbojv2u94v8i2q0l1g916rgh0/033220m5ka00n9a5f1hjsnndnutnc0qd/1582260300000/11572450423408720875/11122016764816395111/1_4DJFfIdAv2wTsbFuCX99h1Gz5BDAfoz?e=download&h=14771753379018855219&authuser=1&nonce=ii1p8hveidr38&user=11122016764816395111&hash=suq09jsn6sh88fjfdqldbqm6fbb3m1o7" -O data/transfer/tatoeba.splits.Feb20.zip -c
unzip tatoeba.splits.Feb20.zip

# Install joeynmt
git clone https://github.com/kervyRivas/joeynmt.git
python joeynmt/setup.py install --force