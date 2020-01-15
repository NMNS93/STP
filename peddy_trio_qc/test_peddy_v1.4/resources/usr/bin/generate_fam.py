#!/usr/bin/env python3
import os
import re
import sys

get_sex = {
    'M':"1", 'F':"2", 'U':"0"
}

def get_relations(all_samples, fam):
    f_id, m_id = "0", "0"
    f_id_match = fam+'-F'
    m_id_match = fam+'-M'
    relations = [ sample for sample in all_samples if fam in sample ]
    for person in relations:
        if re.search(f_id_match, person):
            f_id = person
        elif re.search(m_id_match, person):
            m_id = person
    return f_id, m_id
        
# Read samples
with open(sys.argv[1]) as f:
    all_samples = [ line.strip() for line in f.readlines() ]

for sample in all_samples:
    records = sample.split('_')
    fam, relation = records[8].split('-')
    sex_code = get_sex[records[4]]

    # Record relationships for probands in FAM format
    if relation == 'P':
        f_id, m_id = get_relations(all_samples, fam)
        print("\t".join([fam, sample, f_id, m_id, sex_code, "0"]))
    # Record sex only
    else:
        print("\t".join([fam, sample, "0", "0", sex_code, "0"]))
