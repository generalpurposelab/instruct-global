## GlobalInstruct - a framework for fine-tuning LLMs in low resource languages and an open-source registry of ...

GlobalInstruct is a collection of tools to build instruction datasets, and fine-tune and evaluate LLMs in low resource languages.

## Overview

Fine-tuning LLMs requires building instruction datasets showcasing a diverse set of demonstration conversations to show how to perform a task (often called "few-shot learning"). For example, InstructGPT (the precursor to ChatGPT) was trained on 55k+ examples.

Developing such datasets is difficult in low-resource langauges, because of a scarity of publicly accessible data and the cost of building manually labelled datasets.

rlhf.app leverages lessons from the [self-instruct paper](https://arxiv.org/abs/2212.10560) to build an dataset that combines answers from publicly accessible and verified sources such as Wikipedia and BBC, and synthetic questions created by existing LLMs. While often not performant in low-resource languages, they are often 'good enough' to create a first draft of a question that then can then be verified by human labelers.

## Scripts

The /python folder contains a number of scripts to prepare training datasets and train models. These include:

Data processing:
  - 1_wiki_scrape - scrapes wikipedia in the language of your choice. Wikipedia is currently available in [326 languages](https://meta.wikimedia.org/wiki/List_of_Wikipedias).
  - 2_bbc_scrape.py - scrapes bbc news in the language of your choice. BBC news is currently available in [n languages](https://bbc.com/).
  - 3_clean.py - cleans text so it is suitable for training (e.g. ensuring strings are < 4096 tokens)
  - 4_translate.py - uses LLMs to convert scraped text into a qa dataset

[optional]
    - At this stage, you can manually edit the translations to ensure accuracy (see evaluating models second below)

Model training
  - 5_csv_to_jsonl.py - converts the qa dataset from a csv file to json file (required for finetuning)
  - 6_check.py - checks whether data is suitable for training and calculates cost of training run
  - 7_finetune.py - finetunes openai 3.5 using json file

Evaluations
  - [optional] you can use rlhf.app to create a bank of questions to test your model, or alternatively, you can follow the steps below to use TruthfulQA or other eval datasets
  - 8_TruthfulQA.py - translates truthfulqa (or other provided datasets) into your specified language
  - 9_eval.py - uses truthfulqa to create an eval dataset to evluate your models

## Training models

Different models require different data formats for fine-tuning. This repo uses the format to train OpenAI's models which contain a list of messages where each message has a role, content, and optional name. For example:

```py
{"messages": [{"role": "system", "content": "<system message>"}, {"role": "user", "content": "<prompt text>"}, {"role": "assistant", "content": "<ideal generated text>"}]}
```

## Evaluating models

To evaluate the performance of your model, you can run rlhf.app by visiting [rlhf.app](https://rlhf.app/) or running the repo localling using the following:

```bash
npm install
npm run dev
```

There are various options in the app

## Roadmap
- update 1_wiki_scrape so it ensure text is under n tokens
- update 2_bbc_scrape so it doesn't return headers etc
- update 3_clean.py so it creates one csv file and ensures text is under n tokens
- scrape Igbo (ig) and Nigerian Pidgin (pcm) wiki
- scrape bbc for yoruba, igbo, hausa, and pcm
- clean - change to check for tokens
- translate datasets
- change to check for tokens

due to rounding operations, output may be +- a few extra to input