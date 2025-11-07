# Plagiarism Detection System

## Overview

The **Plagiarism Detection System** is an AI-powered hybrid framework that integrates **automata theory** and **large language models (LLMs)** to identify both **exact** and **semantic** plagiarism. It addresses the increasing demand for reliable plagiarism detection across academic, research, and creative domains.

The system combines **classical string-matching techniques** with **semantic analysis** to detect both **word-for-word copying** and **contextual paraphrasing**, offering a robust and explainable solution for originality verification.

## Mathematical Foundations

### 1. **Aho–Corasick Automaton**

* A **finite-state automaton** for **multi-pattern string matching**.
* Operates in **O(n + m + z)** time, where:

  * *n* = length of text
  * *m* = total length of patterns
  * *z* = number of matches
* Enables efficient detection of repeated or overlapping substrings across large document sets.
* Provides **high-speed** exact overlap detection, crucial for large-scale datasets.

### 2. **Natural Language Processing (NLP)**

* Utilized for **text normalization**, **tokenization**, and **stopword removal**.
* Framework: **NLTK** (Natural Language Toolkit)
* Converts raw text into linguistically meaningful tokens for analysis.
* Supports **syntactic preprocessing** before applying automata and semantic models.

### 3. **Semantic Similarity Analysis**

* Employs **Large Language Models (LLMs)** integrated through **LangChain** and the **Groq API**.
* Expands the topic into relevant subtopics using **generative reasoning**.
* Fetches contextual information from **Wikipedia** for broader concept comparison.
* Measures **semantic similarity** using embeddings and vector-based comparison.
* Detects **paraphrased**, **reworded**, and **conceptually similar** content.

### 4. **Hybrid AI-Automata Integration**

* **Syntactic layer:** Aho–Corasick automaton → detects literal matches.
* **Semantic layer:** LLM-driven similarity scoring → captures idea-level plagiarism.
* The combination ensures both **speed** and **depth**, merging computational efficiency with contextual understanding.

## Methodology

1. **Text Preprocessing**

   * Normalization (lowercasing, punctuation removal)
   * Stopword elimination
   * Tokenization into words/phrases
   * Sentence segmentation for contextual alignment

2. **Syntactic Detection (Aho–Corasick)**

   * Builds a trie-based automaton for multi-pattern search
   * Detects all overlapping or repeated sequences
   * Provides interpretable, location-specific matches

3. **Semantic Detection (LLM + LangChain + Groq)**

   * Topic expansion and contextual reasoning
   * Wikipedia-based knowledge augmentation
   * Embedding similarity for concept-level detection

4. **Reporting**

   * Generates a detailed report showing:

     * Exact overlaps
     * Paraphrased/semantic matches
     * Similarity scores
     * Evaluation metrics (Precision, Recall, F1-Score)

## Tech Stack

| Layer                    | Tools / Technologies Used            |
| ------------------------ | ------------------------------------ |
| **Programming Language** | Python 3.x                           |
| **Libraries**            | NLTK, NumPy, Pandas, Matplotlib      |
| **String Matching**      | Aho–Corasick Automaton               |
| **Semantic Engine**      | LangChain, Groq API                  |
| **External Knowledge**   | Wikipedia API                        |
| **Frontend/UI**          | Streamlit / Flask Dashboard          |
| **Storage**              | Local JSON/SQLite for report storage |
| **Version Control**      | GitHub                               |


## Results

* **Dashboard Interface:** Allows file upload and topic entry
* **Automated Report Generation:** Highlights exact and semantic matches
* **Evaluation Metrics:** Precision, Recall, and F1 score calculated
* **Semantic Example:** Wikipedia-derived context accurately detected rewritten sections

## Key Contributions

* Hybrid **Automata + AI**-based detection system
* Accurate identification of **exact and reworded plagiarism**
* Context-aware topic expansion using LLMs
* Transparent and interpretable detection process
* Scalable and adaptable for different writing styles and domains
