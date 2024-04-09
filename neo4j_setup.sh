# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 09/04/2024

# Install Neo4j on Mac
# brew install neo4j 

# Install Neo4J on Linux (Neo4j requires the Java 17 runtime)
sudo add-apt-repository -y ppa:openjdk-r/ppa  
sudo apt-get update 

## Add the Neo4j repository 
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -  
echo 'deb https://debian.neo4j.com stable latest' | sudo tee -a /etc/apt/sources.list.d/neo4j.list  
sudo apt-get update 

## Install Neo4j 
### Neo4j Community Edition:  
sudo apt-get install neo4j=1:5.12.0  

pip install tqdm
pip install neo4j

### Neo4j Enterprise Edition:  
# sudo apt-get install neo4j-enterprise=1:5.12.0 

## Launch Neo4J server
neo4j start

# Loading Neo4J data
python neo4j_setup.py 