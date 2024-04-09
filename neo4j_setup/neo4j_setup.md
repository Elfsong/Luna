# Neo4J Setup

## Step 1. Make sure you've installed Neo4J.
More detaild can be found on [this document](https://shorturl.at/lyKTZ)

## Step 2. Raw Data Retrieval
Download **data** from [the link](https://mynbox.nus.edu.sg/u/ttsM25_bDPCk2wz1/435f6f30-4a25-4504-b946-c2ecc5aa877c?l).

Place the `Case_Metadata.json` and `Case_Notes.json` to [SOMEWHERE].

## Step 3. Environment Initization
```shell
pip install tqdm
pip install neo4j
neo4j restart
```

## Step 4. Neo4J Data Conversion
```shell
python neo4j_setup.py   -a bolt://localhost:7687 \
                        -u neo4j \
                        -p neo4j \
                        -n [SOMEWHERE]/Case_Notes.json \
                        -m [SOMEWHERE]/data/Case_Metadata.json
```