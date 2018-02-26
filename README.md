# ontologyEvaluate
Entropy-based Ontology Evaluation. 

# Data
We use four ontologies in directory 'dataset', which are saved with owl format. 

# Codes
The source codes are organized in three directories: 'preprocess' involves extracting and building connection matrix; 'embedding' invloves representation learning for nodes in ontologies; 'entropy-calculate' invloves calculating entropy from embeddings and connection matrixes.

# Requirements
- Python (>=3.5)
- TensorFlow (>=1.4)
- scikit-learn (>=0.18)
- Matplotlib (>=2.0.0)
- NVIDIA Graph Analytics library (calculating shortest pathes for the large-scale ontology: antiBio)
