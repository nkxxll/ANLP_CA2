<div align="center">

<h1>Text Analysis of Steam Reviews</h1>

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Jupyter Notebook](https://img.shields.io/badge/jupyter-%23FA0F00.svg?style=for-the-badge&logo=jupyter&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=for-the-badge&logo=PyTorch&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)
![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)

<h4>Advanced Natural Language Processing - WS 2024/25</h4>

_Jessica Benker, Cedric Mingham, Maximilian Kühn, Marcel Kohl, Niklas Kirschall_

</div>

> [!NOTE]  
> Code and Results for CA1 can be found in the [CA1 repository](https://github.com/maxikuehn/ANLP_WS24).

## Structure

```
├── README.md <-- you are here
├── data
├── docs
├── models
└── src
```

The structure of this repos is as follows. `src` holds all the code. `docs` holds any additionally
information that is not yet ready to be written in the documentation. `data`
holds all the data and models that will be relevant for the project.

## Installation

Use a `venv` if you want.

```sh
conda install --yes --file requirements.txt
# or if you like your live challenging
pip install -r requirements.txt
```

## Execute the code

The notebooks containing the results of the binary classification can be found in `src/name_here`.
The results for the multi-label classification can also be found in the `src` folder.

- `ffn_review_classifier.ipynb` todo short description
- `gru_review_classifier.ipynb` todo short description
- `gru_topics_classifier.ipynb` todo short description

The script for the automated annotation of steam reviews is located in the
`src/scripts/ollama_topic_classification.py` and `src/scripts/ollama_topic_annotator.py` files.
These scripts should be executed from the `src/scripts` directory to make sure that the relative
path to the data files is right. The first script holds a class for the automated annotation and
parsing of the answers from the LLMs while the second script was used to annotate a large set of
reviews as training data for the multi-label classification neural network.  
For the evaluation of the results from the automated annotation you can use the
`src/scripts/evaluate.py`, `src/example_multilabel_classification_evaluation.ipynb`,
`src/model_comparison.ipynb` and `src/scripts/multilabel_classification_evaluator.py`. The latter
holds the core functionality of the evaluation and the first two scripts use this core
functionality. The third script is a notebook that compares the results of the different
LLMs visually.
