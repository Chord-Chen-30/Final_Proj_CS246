# Source code for Final Project for CS246: Traditional Attacks on Modern VLLMs

## Intro
<p align=center>
    <img src="figs/intro.jpg" alt="加载失败 请尝试刷新" width="300" />
</p>

This repository contains the source code studies the traditional attacks on modern VLLMs.
- Tradition image-side attack: $L_1$,$L_{inf}$-bounded PGD attack
<p align=center style="padding-left: 50px;">
    <img src="figs/case.jpg" alt="加载失败 请尝试刷新" width="500" />
</p>

- Prompt-side attack: 
  - Special token
  - Ignore image content
  - Poison content
  - Force instructions
  - Role-playing
<p align=center style="padding-left: 50px;">
    <img src="figs/case2.jpg" alt="加载失败 请尝试刷新" width="500" />
</p>

- Mixed attack


## Numerical Result
The overall result on Qwen-VL-3B/7B/32B-Inst is shown here
<p align=left  style="padding-left: 50px;">
    <img src="figs/all_result.jpg" alt="加载失败 请尝试刷新" width="600" />
</p>

## Code
- attack.ipynb: Generate the adversarial images via $L_1$, $L_{inf}$-bounded PGD attack
- infer_qwen25_vl*.py: Run inference of Qwen2.5-VL series on different adversarial inputs
- mmmu_cls/ : Data 
  - make_data.py: Resize image and extract dataset this work uses from origin MMMU dataset (You'll not need to run it).

## Example
```bash
conda create -n att python=3.10
conda activate att
pip install -r requirements.txt
python infer_qwen25_vl_text_att.py # Evaluate the prompt-side text attack
python infer_qwen25_vl_mix_att.py # Evaluate the mixed attack, with data properly prepared.
```

## Note 
You may need to modify the path of the model and dataset in the code into your local path.

Welcome to contact me if you have any questions.