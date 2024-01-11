# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 29/12/2023

import pandas as pd
from collections import defaultdict

def banner():
    with open('./data/banner', 'r') as banner_f:
        print(banner_f.read())

def get_product_mapping(file_path: str) -> dict:
    df = pd.read_excel(file_path)
    p_mapping = defaultdict(lambda: defaultdict(lambda: list()))

    for _, row in df.iterrows():
        tech = row["Technology_Text__c"]
        sub_tech = row["Sub_Technology_Text__c"]
        p = row["Product_Name__c"]
        p_mapping[tech][sub_tech] += [str(p)]
        
    return p_mapping

def save_results(df: pd.DataFrame, file_path: str) -> None:
    df.to_csv(file_path)