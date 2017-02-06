# Scripts to index sample bioinformatics datasets with Elasticsearch 

Inspired by the [nosql-tests](https://github.com/weinberger/nosql-tests/)
project we want to develop scripts for NoSQL indexing and querying of
sample bioinformatics datasets.
We are in early stages of the project and we have scripts for 5 sample datasets

* PubChem BioAssay json files: ftp://ftp.ncbi.nlm.nih.gov/pubchem/Bioassay/JSON
* WikiPathways gpml files: http://www.wikipathways.org/index.php/Download_Pathways
* PMC articles: ftp://ftp.ebi.ac.uk/pub/databases/pmc/manuscripts
* Ensembl regulatory build GFF files: ftp://ftp.ensembl.org/pub/release-87/regulation/homo_sapiens
* NCBI PubTator gene2pub mapping: ftp://ftp.ncbi.nlm.nih.gov/pub/lu/PubTator

### Notes on PMC articles

[index-pmc-articles.py](index-pmc-articles.py) reads and indexes archives of PMC articles xml files.
```
git clone https://github.com/titipata/pubmed_parser.git
sudo python3 setup.py install

sudo pip3 install --upgrade git+https://github.com/titipata/pubmed_parser.git
pip3 install --user git+https://github.com/titipata/pubmed_parser.git
```
### Notes on PubTator datasets 

[index-pubtator-files.py](index-pubtator-files.py) reads and indexes NCBI
PubTator gene2pub mappings

TODO:

* Support for all PubTator mappings

### Notes on PubChem dataset

[index-pubchem-bioassays.py](index-pubchem-bioassays.py) reads and indexes
the zipped and compressed PubChem BioAssay json files,
without extracting them to temporary files.

TODO:

* Support for entries larger than 800mb
* Use bulk indexer
* Mappings for Elasticsearch 2
* Python2 support

### Notes on WikiPathways datasets

[index-wikipathways.py](index-wikipathways.py) reads and indexes
the zipped WikiPathways gpml files,
without extracting them to temporary files.

### Elasticsearch server settings
Since some of the PubChem BioAssay json files are large we need to change
few Elasticsearch default settings to higher values:

* Heap memory

    * _Elasticsearch-5_: Set `-Xms` AND `-Xmx` JVM settings to at least 14 GB,
    in configuration file `config\jvm.options`

    * _Elasticsearch-2_: Set `ES_MIN_MEM` AND `ES_MAX_MEM` environment variables to at least 1 and 14 GBs,
    (defaults are 256mb and 1GB), before calling your Elasticsearch server
    start script `bin\elasticsearch`

* Set `http.max_content_length: 800mb`, default 100mb,
  in your Elasticsearch configuration file `config/elasticsearch.yml`
* Large entries mean much garbage collection activity;
  [make sure garbage collection is fast](https://www.elastic.co/guide/en/elasticsearch/reference/current/setup-configuration-memory.html) 
  by preventing any Elasticsearch memory from being swapped out
  

### Datasets we are considering to include: 
* Kegg?, Biocyc?, REACTOME?, Rhea?
* Gene names and synonyms?
* Sample sequence similarity search results, in BLAST xml2 and SAM formats?

## Copyright
NoSQL-biosets project have been developed as part of other projects in King Abdullah University of Science
and Technology (http://www.kaust.edu.sa)