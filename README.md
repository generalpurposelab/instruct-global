# Instruct-Global

Instruct-global automates the process of generating instruction datasets in low-resource languages (LRLs). 

## Background

Language models (LMs) like GPT-4 and LLaMa 2 produce below-par performance in LRLs, particularly on generative tasks (Ojo, Ogueji, Stenetorp, and Adelani., 2023), and are encoded with Western values (Durmus et al, 2023). 

Poor LM performance in LRLs has broader safety implications e.g. translating unsafe English inputs into LRLs have been shown to circumvent LM safeguards (Yong et al., 2023), something we have observed in our own work.

Instruction fine-tuning has been shown to improve usability (Chung et al., 2022b;; Zhang et al., 2023b; Jiang et al., 2023), multilingual performance (Nguyen et al., 2023; OpenAI, 2023), and embed cultural values (Durmus et al, 2023) within pretrained LMs.

Constructing human-written instruction data can be expensive, time-consuming and lacking diversity (Ouyang et al., 2022). LMs have been successfully used to self-generate instructions in English (Wang et al, 2023), and show promise at translation for LRLs (Kadaoui et al 2023) with as few as 40 examples shown to improve multilingual instruction-following (Shaham et al, 2024).

## Our Solution

Inspired by automatic instruction generation including InstructGPT (Ouyang et al., 2022), Self-Instruct (Wang et al., 2023), and Stanford’s Alpaca (Taori et al., 2023), instruct-global combines self-instruct, machine translation with human-in-the-loop (HITL) to transform preexisting high quality datasets (e.g. classification, summarisation etc) into instruction datasets in order to fine tune LMs.

### How It Works

1. **Data Preparation**: Users input existing data and define a schema detailing the transformation process, including task categories, dataset size, and target languages.
2. **Schema Mapping**: The input schema is aligned with task categories from established models like InstructGPT.
3. **Pipeline Processing**:
   - Creation of 'skeleton questions' in English with placeholders for data insertion.
   - Evaluation of the skeleton dataset's quality.
   - Translation of skeleton questions into the target LRL.
   - Substitution of placeholders with actual data from the input datasets.
4. **Output Generation**: The process culminates in a CSV file containing the instructional content, translations, and task metadata.

## Getting Started

### Prerequisites

- An OpenAI API key for GPT model access.
- A Google Cloud project with the Translation API enabled and credentials configured.

### Setup

1. Clone the repository and navigate to the project directory.
2. Install dependencies with `pip install -r requirements.txt`.
3. Configure your OpenAI API key and Google Cloud project ID in `run.py` and add you google credentials file as `cred.json` in the project directory.
4. Define your input schema in `/input/input_schema.csv` and add your data files. See `/examples` for guidance.

### Usage

Run `python run.py` to initiate the dataset generation and translation process.

```
pip install -r requirements.txt
python run.py
```

## Challenges and Considerations

- Machine translation errors and their propagation.
- Increased training and inference costs for text with diacritics.
- The necessity of local knowledge for identifying reliable sources.
- Safety and ethical considerations in dataset generation.

## Roadmap

- Add NLLB and MADLAD

## Authors

This library is created by [Equiano Institute](https://equiano.institute), [Masakhane](https://www.masakhane.io/), and [General Purpose](https://general-purpose.io) team members.