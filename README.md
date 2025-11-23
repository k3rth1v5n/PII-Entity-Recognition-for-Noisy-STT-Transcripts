# PII NER Assignment Skeleton

This repo is a skeleton for a token-level NER model that tags PII in STT-style transcripts.


The whole out folder for my model can be downloaded from: https://drive.google.com/file/d/1oOqdL9kDpWPczOdN6IoYnsrXv9wNDSiB/view?usp=sharing
## Setup

```bash
pip install -r requirements.txt
```

## Train

```bash
python3 src/train.py \
  --model_name distilbert-base-uncased \
  --train data/train.jsonl \
  --dev data/dev.jsonl \
  --out_dir out
```

## Predict

```bash
python3 src/predict.py \
  --model_dir out \
  --input data/dev.jsonl \
  --output out/dev_pred.json
```

## Evaluate

```bash
python3 src/eval_span_f1.py \
  --gold data/dev.jsonl \
  --pred out/dev_pred.json
```

## Measure latency

```bash
python3 src/measure_latency.py \
  --model_dir out \
  --input data/dev.jsonl \
  --runs 50
```

Your task in the assignment is to modify the model and training code to improve entity and PII detection quality while keeping **p95 latency below ~20 ms** per utterance (batch size 1, on a reasonably modern CPU).
