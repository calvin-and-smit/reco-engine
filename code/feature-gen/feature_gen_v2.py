import os
os.chdir('/home/windr/GitHub/reco-engine/code/feature-gen')
import sys
sys.path.append('../scraping')
sys.path.append('../tools')

import db_connect
from pprint import pprint
from copy import deepcopy
from collections import Counter


def feat_gen_directors(director_list: list):
    # Read DB_cred from global
    global db_cred_prod, db_cred_prod

    # Create data_to_insert template dictionary for faster IO
    dti_template = dict((f"Dir_{director.replace(' ','-')}", 0) for director in director_list)

    # Generate Directors feature
    with db_connect.get_collection(db_cred_prod).find({}) as prod_data:
        for row in prod_data:
            # Use Deepcopy to create a 'deep' copy from dti_template
            # Reference: https://thispointer.com/python-how-to-copy-a-dictionary-shallow-copy-vs-deep-copy/
            data_to_insert = deepcopy(dti_template)
            # Check directors one by one
            if 'MI_Director' in row:
                for director in row['MI_Director']:
                    if director in important_directors:
                        data_to_insert[f"Dir_{director.replace(' ','-')}"] = 1
                    continue
            # Insert data into features collection in the database
            # Option upsert=True is necessary; Equivalent to 'insert or update if exists'
            db_connect.get_collection(db_cred_feat).update_one({'_id': row['_id']},
                                                               {'$set': data_to_insert},
                                                               upsert=True)
            # Verifying output
            # pprint(data_to_insert)
            continue
    return


def feat_gen_genre():
    # Read DB_cred from global
    global db_cred_prod, db_cred_prod

    # Load unique genre codes from production dataset
    gen_code_list = set()
    with db_connect.get_collection(db_cred_prod).find({}) as prod_data:
        for row in prod_data:
            for genre in row['MI_Genre']:
                gen_code_list.add(genre)

    # Create data_to_insert template
    dti_template = dict((f'Genre_{gen_code}', 0) for gen_code in gen_code_list)

    # Generate Genre feature
    with db_connect.get_collection(db_cred_prod).find({}) as prod_data:
        # Check Genre for each row & insert to the database
        for row in prod_data:
            data_to_insert = deepcopy(dti_template)
            for genre in row['MI_Genre']:
                data_to_insert[f'Genre_{genre}'] = 1
            # Insert data into features collection in the database
            db_connect.get_collection(db_cred_feat).update_one({'_id': row['_id']},
                                                               {'$set': data_to_insert},
                                                               upsert=True)
            # Verifying output
            # pprint(data_to_insert)
    return


if __name__ == '__main__':

    # Define database details
    db_cred_prod = ['../../connection-details/db-reco-engine.credential',
                    'reco-engine', 'production']
    db_cred_feat = ['../../connection-details/db-reco-engine.credential',
                    'reco-engine', 'features']

    # Obtain unique directors as a Counter() object from production collection in the database
    with db_connect.get_collection(db_cred_prod).find({}) as production_data:
        # Obtain unique directors list
        unique_directors = Counter()
        for line in production_data:
            if 'MI_Director' in line:
                for dirctr in line['MI_Director']:
                    unique_directors[dirctr] += 1
    # Define important directors
    # (Using the top 20 most common directors extracted from database for now)
    important_directors = list(item[0] for item in unique_directors.most_common(20))

    # Generate director feature
    feat_gen_directors(director_list=important_directors)

    # Generate Genre feature
    feat_gen_genre()
