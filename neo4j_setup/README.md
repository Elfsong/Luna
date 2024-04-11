# Neo4J Setup

## Step 1. Make sure you've installed Neo4J.
More details can be found on [this document](https://shorturl.at/lyKTZ)

## Step 2. Raw Data Retrieval
* Download `Case_Metadata.json` and `Case_Notes.json` from [the link](https://mynbox.nus.edu.sg/u/ttsM25_bDPCk2wz1/435f6f30-4a25-4504-b946-c2ecc5aa877c?l).
Password can be found [here](mailto:mingzhe@nus.edu.sg)

* OR you can use your own `Case_Metadata.json` and `Case_Notes.json`.

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
                        -m [SOMEWHERE]/Case_Metadata.json
```
