# Code and documentation for instruct-global.

## Datasets for Yoruba

### Pre-training

| Source         | Description                                              | Source(s)           | Clean? | Tokens (M) |
|----------------|----------------------------------------------------------|---------------------|--------|------------|
| Common Crawl   | Audited version of CommonCrawl + additional verified news sources | Wura              | Y      | 82.6       |
| Wikipedia      | Yoruba Wiki                                              | Scraping wiki       | Y      | 0.85       |
| News           | Articles from Alaroye, Asejere, Awikonko, BBC, VON, Yoruba Global Voices | African news corpus | Y      | 16         |
| Twitter        | Tweets                                                   | AfriSenti           | N      | 0.4        |
| Religious texts| NIV and KJV versions of the bible                        | Niger-Volta-LTI     | Y      | 5          |
|                | Book of Mormon                                           |                     | Y      | 1          |
|                | JW                                                       |                     | N      | 30.86      |
| Other          | Nollywood movie reviews                                  |                     | Y      | 0.05       |
|                | Yoruba blog                                              |                     | Y      | 0.05       |
|                | Yoruba Proverbs                                          |                     | Y      | 0.09       |
|                | Books                                                    |                     | N      | 0.36       |
|                |                                                          |                     |        |            |
|                | Total                                                    |                     |        | 137.26     |

### Fine-tuning

| Type           | Description                                             | Source       | Number |
|----------------|---------------------------------------------------------|--------------|--------|
| Various        |                                                         | Alpaca_GPT_4 | 51787  |
| Open QA        | Cross-lingual question answering (QA) dataset with a focus on African languages | AfriQA       | 823    |
| Summarization  | Professionally annotated article-summary pairs from BBC | XLSum        | 7940   |
| Translation    | Translation dataset with questions                      | MENYO-20k    | 213    |
|                |                                                         |              |        |
| Total          |                                                         |              | 60763  |

