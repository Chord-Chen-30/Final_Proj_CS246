import json
import re
from pprint import pprint
import shutil
import os
from tqdm import tqdm


def copy_image(source_path, target_path):
    shutil.copyfile(source_path, target_path)

def id2label(s):
    match = re.match(r'^(?:dev|validation)_(.+?)_\d+$', s)
    if match:
        print(match.group(1))
        return match.group(1)
    else:
        print(s, 'get label Error')
        exit()

labels_to_keep = ('Accounting', 'Agriculture', 'Art', 'Electronics', 'Music')

label_stat = dict()
label2id = dict()
label_start = 0
with open('/mnt/nas-alinlp/zhuochen.zc/others/cs246/raw_mmmu/mmmu/dev_oss.all.jsonl') as f:
    data = [json.loads(line) for line in f]

with open('/mnt/nas-alinlp/zhuochen.zc/others/cs246/raw_mmmu/mmmu/val_oss.all.jsonl') as f:
    data += [json.loads(line) for line in f]

with open('./mmmu_cls.jsonl', 'w') as g:

    for d in tqdm(data):
        label = id2label(d['question_id'])
        
        if label not in labels_to_keep:
            continue

        if label not in label_stat:
            label_stat[label] = 0
            label2id[label] = label_start
            label_start += 1
        else:
            label_stat[label] += 1

        d['label'] = label
        d['label_id'] = label2id[label]
        
        new_path = os.path.join("image", os.path.basename(d['image_path']))
        source_path = os.path.join("/mnt/nas-alinlp/zhuochen.zc/others/cs246/raw_mmmu/mmmu_image", os.path.basename(d['image_path']))

        copy_image(source_path, new_path)
        d['image_path'] = os.path.join('mmmu_cls', new_path)

        g.write(json.dumps(d) + '\n')

pprint(label_stat)
pprint(f"# CLS: {len(label_stat)}")