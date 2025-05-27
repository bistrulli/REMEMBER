# Replication Package for "Stochastic Conformance Checking based on Variable-length Markov Chains"

This replication package contains all the necessary files and instructions to replicate the experiments described in the paper: **"Stochastic Conformance Checking based on Variable-length Markov Chains"**.

---

## Table of Contents
- [Directory Structure](#directory-structure)
- [Setup Instructions](#setup-instructions)
- [How to Run the Experiments](#how-to-run-the-experiments)
- [File Descriptions](#file-descriptions)

---

## Directory Structure

```
replication_package/
├── data/                  # Contains input data for experiments
├── likelyhood/            # Results and likelihood computation files
├── plots/                 # Folder containing the final plots as pdf files
├── replicateExp.ipynb     # Main notebook to replicate experiments
├── requirements.txt       # Python dependencies
├── scripts/               # Utility scripts for processing
└── vlmcProcessMining.py   # Main script for the VLMC implementation
```

---

## Setup Instructions

### Prerequisites
Ensure you have the following installed:
- Python (>= 3.8)
- `pip` (Python package manager)
- `Java` (>= 17)

### Step 1: Install Dependencies
Navigate to the root of the package and install the required dependencies using the following command:
```bash
pip install -r requirements.txt
```

Alternatively, you can create a virtual environment:
```bash
python -m venv replenv
source replenv/bin/activate   # On Windows, use: replenv\Scripts\activate
pip install -r requirements.txt
```

---

## How to Run the Experiments

1. **Run the Jupyter Notebook**  
   Open `replicateExp.ipynb` to run the experiments interactively. Execute each cell sequentially for full replication.

   To launch Jupyter Notebook:
   ```bash
   jupyter notebook
   ```

2. **Data and Outputs**  
   - Input data is stored in the `data/` folder.
   - Intermediate likelihood computations are in the `likelyhood/` folder.
   - Generated plots are stored in the `plots/` folder.


### Key Files
- **`replicateExp.ipynb`**  
  The Jupyter Notebook for reproducing the experiments interactively.

- **`requirements.txt`**  
  Lists the Python libraries and dependencies required to run the package.

- **`vlmcProcessMining.py`**  
  The main implementation of the Variable-length Markov Chains process mining algorithm.

---

## Notes
- For issues or further clarification, please contact [emilio.incerto@imtlucca.it].
- Ensure proper Python version and dependencies are installed to avoid compatibility issues.
- Feel free to explore and modify scripts for additional experimentation.

---

## Citation
If you use this package, please cite the original paper:
```
Stochastic Conformance Checking based on Variable-length Markov Chains
```

---
