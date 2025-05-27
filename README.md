# REMEMBER: Uncovering Complex Temporal Dependencies in Process Logs with Variable Length Markov Chains

This repository contains the source code and necessary files for **REMEMBER**, a tool for analyzing process logs and uncovering complex temporal dependencies using Variable Length Markov Chains (VLMCs). This work has been submitted to the 23rd International Conference on Business Process Management (BPM 2025) under the title: "REMEMBER: Uncovering Complex Temporal Dependencies in Process Logs with Variable Length Markov Chains".

---

## Table of Contents
- [Overview](#overview)
- [Directory Structure](#directory-structure)
- [Setup Instructions](#setup-instructions)
- [How to Use REMEMBER](#how-to-use-remember)
- [File Descriptions](#file-descriptions)
- [Citation](#citation)
- [Contact](#contact)

---

## Overview

REMEMBER is a Python-based tool that implements algorithms for process mining using VLMCs. It allows users to:
- Process event logs (e.g., in XES format, CSV).
- Mine VLMC models from these logs.
- Compute likelihood of traces based on the mined models.
- Perform conformance checking and other advanced analyses.

The core logic is implemented in `vlmcProcessMining.py` and utilizes external Java libraries for specific VLMC operations.

---

## Directory Structure

```
.
├── .git/                  # Git version control files
├── .gitignore             # Specifies intentionally untracked files that Git should ignore
├── LICENSE                # License file for the project
├── README.md              # This README file
├── replicateExp.ipynb     # Jupyter Notebook with examples and experimental replications
├── requirements.txt       # Python dependencies
├── scripts/               # Contains utility scripts and Java archives (JARs) used by REMEMBER
│   └── jfitVlmc.jar       # Java archive for VLMC fitting and likelihood computation
│   └── trace2ecf.jar      # Java archive for trace conversion
└── vlmcProcessMining.py   # Main Python script implementing the REMEMBER tool
```

---

## Setup Instructions

### Prerequisites
Ensure you have the following installed:
- Python (>= 3.8)
- `pip` (Python package manager)
- Java (>= 17) (Ensure `java` is in your system's PATH)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd REMEMBER # Or your chosen directory name
```

### Step 2: Install Dependencies
Navigate to the root of the repository and install the required Python dependencies:
```bash
pip install -r requirements.txt
```

It's recommended to use a virtual environment:
```bash
python -m venv venv
source venv/bin/activate   # On Windows, use: venv\Scripts\activate
pip install -r requirements.txt
```

---

## How to Use REMEMBER

The `vlmcProcessMining.py` script provides the core functionalities of REMEMBER. You can import and use its functions within your own Python scripts or explore its usage in the `replicateExp.ipynb` Jupyter Notebook.

### Key functionalities in `vlmcProcessMining.py`:
- `processData(inputFile, idCol, activityCol)`: Processes raw CSV data into a trace format suitable for VLMC.
- `processXesFile(inputFile, idCol, activityCol, timestapCol)`: Processes XES files.
- `mineProcess(ecfFile, outFile, infile, vlmcfile, ...)`: Mines a VLMC model from an event log.
- `getLikelyhood(ecfFile, outFile, infile, vlmcfile, ..., traces, vlmc, cwd)`: Computes the likelihood of traces given a VLMC model.
- `convertTrace(inputFile, outputFile)`: Converts traces to ECF format using `trace2ecf.jar`.

### Running Examples with the Jupyter Notebook
1.  **Launch Jupyter Notebook:**
    ```bash
    jupyter notebook
    ```
2.  Open `replicateExp.ipynb`. This notebook contains various examples demonstrating how to:
    - Load and preprocess event logs.
    - Mine VLMC models.
    - Calculate likelihoods.
    - Replicate experiments from the associated paper.

---

## File Descriptions

- **`README.md`**: This file, providing an overview of the REMEMBER tool and instructions.
- **`vlmcProcessMining.py`**: The core Python script containing the implementation of the REMEMBER tool, including functions for data processing, VLMC model mining, likelihood computation, and conformance checking.
- **`replicateExp.ipynb`**: A Jupyter Notebook that demonstrates the usage of `vlmcProcessMining.py` for various tasks, including replicating experiments. It serves as a practical guide and example set.
- **`requirements.txt`**: Lists the Python libraries and their versions required to run the REMEMBER tool and the example notebook.
- **`scripts/`**: This directory contains external Java archives (JARs) that are essential for the VLMC functionalities:
    - `jfitVlmc.jar`: Used for fitting VLMC models and computing likelihoods.
    - `trace2ecf.jar`: Used for converting event log traces into the ECF (Event Collection Format) required by `jfitVlmc.jar`.
- **`LICENSE`**: Contains the licensing information for this software.
- **`.gitignore`**: Specifies files and directories that Git should ignore.

---

## Citation
If you use REMEMBER in your research or work, please cite our paper (once published):

```
REMEMBER: Uncovering Complex Temporal Dependencies in Process Logs with Variable Length Markov Chains
(Submitted to BPM 2025)
```
You can also refer to the original paper that introduced the VLMC-based stochastic conformance checking:
```
Stochastic Conformance Checking based on Variable-length Markov Chains
```

---

## Contact
For issues, questions, or further clarification, please contact [emilio.incerto@imtlucca.it].

---
