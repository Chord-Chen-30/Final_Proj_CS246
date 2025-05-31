from modelscope import Qwen2_5_VLForConditionalGeneration, AutoTokenizer, AutoProcessor, snapshot_download
from qwen_vl_utils import process_vision_info
import json
from prompt import PROMPT_IMAGE_CLS
from prompt import (PROMPT_IMAGE_CLS_ATT_SPECIAL_TOKEN, 
                    PROMPT_IMAGE_CLS_ATT_IGNORE_IMAGE, 
                    PROMPT_IMAGE_CLS_POISON,
                    PROMPT_IMAGE_CLS_ATT_FORCE_INSTRUCTION,
                    PROMPT_IMAGE_CLS_ATT_ROLE)

from tqdm import tqdm


# model_path = snapshot_download("Qwen/Qwen2.5-VL-3B-Instruct", cache_dir="/mnt/nas-alinlp/zhuochen.zc/models")
# model_path = "/mnt/nas-alinlp/zhuochen.zc/models/Qwen/Qwen2___5-VL-3B-Instruct"
# model_path = "/mnt/nas-alinlp/zhuochen.zc/models/Qwen/Qwen2___5-VL-7B-Instruct"

model_path = snapshot_download("Qwen/Qwen2.5-VL-32B-Instruct", cache_dir="/mnt/nas-alinlp/zhuochen.zc/models")


model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    model_path, torch_dtype="auto", device_map="auto"
)

# We recommend enabling flash_attention_2 for better acceleration and memory saving, especially in multi-image and video scenarios.
# model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
#     "Qwen/Qwen2.5-VL-3B-Instruct",
#     torch_dtype=torch.bfloat16,
#     attn_implementation="flash_attention_2",
#     device_map="auto",
# )

# default processer
processor = AutoProcessor.from_pretrained(model_path)

# The default range for the number of visual tokens per image in the model is 4-16384.
# You can set min_pixels and max_pixels according to your needs, such as a token range of 256-1280, to balance performance and cost.
# min_pixels = 256*28*28
# max_pixels = 1280*28*28
# processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-3B-Instruct", min_pixels=min_pixels, max_pixels=max_pixels)

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "image",
                "image": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg",
            },
            {"type": "text", "text": "Describe this image."},
        ],
    }
]

def inference(text: str, image: str):
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": image,
                },
                {"type": "text", "text": text},
            ],
        }
    ]
    text = processor.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    )
    inputs = inputs.to("cuda")
    generated_ids = model.generate(**inputs, max_new_tokens=128)
    generated_ids_trimmed = [
        out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    output_text = processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )

    return output_text[0]


image_attacks = ['l1', 'linf']
steps = [1, 3, 5, 10]


text_attacks = {
    'special_token': PROMPT_IMAGE_CLS_ATT_SPECIAL_TOKEN,
    'ignore_image': PROMPT_IMAGE_CLS_ATT_IGNORE_IMAGE,
    'poison': PROMPT_IMAGE_CLS_POISON,
    'force_inst': PROMPT_IMAGE_CLS_ATT_FORCE_INSTRUCTION,
    'role': PROMPT_IMAGE_CLS_ATT_ROLE
}

print_str = ""

for image_attack in image_attacks:
    for step in steps:

        for text_attack in text_attacks:
            PROMPT_IMAGE_CLS = text_attacks[text_attack]

            if image_attack == 'l1':
                c = 1e8
            else:
                c = 1

            # print_str += f"{text_attack}\t{image_attack}\t{step}\t"

            print(f'attack: {image_attack}, c: {c}, step: {step}')
            acc = 0.
            label_acc = {}

            with open('mmmu_cls/mmmu_cls_resized.jsonl') as f:
                lines = f.readlines()
                for line in tqdm(lines, ncols=100, leave=False, ascii=True):
                    data = json.loads(line)
                    image = data['image_path']
                    image = image.replace('resized_image', f'{image_attack}_att_image_{c}_{step}')
                    
                    label = data['label']
                    question = data['question']

                    if text_attack == 'special_token':
                        text = PROMPT_IMAGE_CLS.format(question=question, special_token="<|end-of-text|> <|imagine|>")
                    else:
                        text = PROMPT_IMAGE_CLS.format(question=question)

                    output_text = inference(text, image)

                    correct = label.lower().strip() in output_text.lower().strip()
                    # tqdm.write(f"({label}) {output_text}, {str(correct)}")

                    if label not in label_acc:
                        label_acc[label] = []
                    
                    if correct:
                        acc += 1
                        label_acc[label].append(1)
                    else:
                        label_acc[label].append(0)

            for k in label_acc:
                label_acc[k] = round(sum(label_acc[k])/len(label_acc[k])*100,2)

            print(label_acc)
            print(f'{acc}/{len(lines)} = {acc/len(lines)*100:.2f}')
            print('='*50)

            print_str += f"{acc/len(lines)*100:.2f}\t"
        print_str += '\n'


with open('print32b.output', 'w') as f:
    f.write(print_str)
