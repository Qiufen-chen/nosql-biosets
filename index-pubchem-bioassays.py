#!/usr/bin/python3

import argparse
import gzip
import json
import os
import time
from zipfile import ZipFile
from elasticsearch import Elasticsearch


# Read PubChem Bioassays json files, index using the index function specified
# Iterate over files in the folder if the input file is a folder
def read_and_index_pubchem_bioassays(infile, es, indexfunc):
    print("Reading %s " % infile)
    i = 0
    t1 = time.time()
    if os.path.isdir(infile):
        for child in os.listdir(infile):
            c = os.path.join(infile, child)
            if child.endswith(".zip"):
                read_and_index_pubchem_bioassays_zipfile(c, es, indexfunc)
            else:
                read_and_index_pubchem_bioassays_file(c, es, indexfunc)
            i += 1
    else:
        if infile.endswith(".zip"):
            read_and_index_pubchem_bioassays_zipfile(infile, es, indexfunc)
        else:
            read_and_index_pubchem_bioassays_file(infile, es, indexfunc)
        i = 1
    t2 = time.time()
    print("-- %d files have been processed, in %dms"
          % (i, (t2 - t1) * 1000))
    return None


# Read PubChem Bioassays zip file, index using the index function specified
def read_and_index_pubchem_bioassays_zipfile(zipfile, es, indexfunc):
    print("\nProcessing %s " % zipfile)
    i = 0
    r = 0
    with ZipFile(zipfile) as myzip:
        for fname in myzip.namelist():
            aid = fname[fname.find('/')+1:fname.find(".json")]
            # check whether the entry is already indexed
            if not es.exists(index=args.index, doc_type='bioassay', id=aid):
                with myzip.open(fname) as jfile:
                    f = gzip.open(jfile, 'rt')
                    r = indexfunc(es, f, r, aid)
                    i += 1
            else: print("-", end='', flush=True)
    return i


# Read PubChem Bioassays file, index using the index function specified
def read_and_index_pubchem_bioassays_file(infile, es, indexfunc):
    if infile.endswith(".gz"):
        f = gzip.open(infile, 'rt')
    else:
        f = open(infile, 'r')
    aid = infile[infile.rfind('/') + 1:infile.find(".json")]
    r = indexfunc(es, f, 0, aid)
    return r


def update_date(date):
    d = "{}-{}-{}".format(date["std"]["year"], date["std"]["month"],
                          date["std"]["day"])
    del (date["std"])
    return d


def update_dates(doc):
    for data in doc["PC_AssaySubmit"]["data"]:
        date = data["date"]
        d = update_date(date)
        data["date"] = d
    db = doc["PC_AssaySubmit"]["assay"]["descr"]["aid_source"]["db"]
    if "date" in db:
        d = update_date(db["date"])
        doc["PC_AssaySubmit"]["assay"]["descr"]["aid_source"]["db"]["date"] = d
    return


def es_index_bioassay(es, f, r, aid_):
    doc = json.load(f)
    # TODO: support for large entries, >800mb; ex:0540001_0541000/540253.json.gz
    if f.tell() < 800400400:
        update_dates(doc)
        aid = doc['PC_AssaySubmit']['assay']['descr']['aid']['id']
        if str(aid) != aid_:
            print("filename and Assay ids not same, please check '%s' vs '%s'"
                  % (aid, aid_))
            return r
        try:
            if r>0 and (r+f.tell() > 6666*12):  # refresh as needed
                print("r", end='', flush=True)
                es.indices.refresh(index=args.index)
                es.indices.clear_cache(index=args.index)
                r = 0
            print(".", end='', flush=True)
            es.index(index=args.index, doc_type='bioassay',
                     id=aid, body=json.dumps(doc))
            r += f.tell()
        except Exception as e:
            print(e)
    else:
        print("large entry %s %d" % (aid_, f.tell()))
    return r


def main(es, infile, index):
    es.indices.delete(index=index, params={"timeout": "10s"})
    iconfig = json.load(open("pubchem-bioassays-index-config.json", "rt"))
    es.indices.create(index=index, params={"timeout": "20s"},
                      ignore=400, body=iconfig, wait_for_active_shards=1)
    read_and_index_pubchem_bioassays(infile, es, es_index_bioassay)
    es.indices.refresh(index=index)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Index PubChem Bioassays, using Elasticsearch')
    parser.add_argument('--infile',
                        # default="./data/pubchem-samplefiles/bioassays",
                        # default="/reference/NCBI/pubchem/Bioassay/JSON/",
                        default="/reference/NCBI/pubchem/Bioassay/JSON/1158001_1159000.zip",
                        help='input file to index')
    parser.add_argument('--index',
                        default="pubchem-bioassays-test15",
                        help='name of the elasticsearch index')
    parser.add_argument('--host', default="esnode-khadija",
                        help='Elasticsearch server hostname')
    parser.add_argument('--port', default="9200",
                        help="Elasticsearch server port")
    args = parser.parse_args()
    host = args.host
    port = args.port
    con = Elasticsearch(host=host, port=port, timeout=3600)
    main(con, args.infile, args.index)
