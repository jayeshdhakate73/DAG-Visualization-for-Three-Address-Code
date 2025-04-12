# DAG Construction and Heuristic-Based Optimization from Three-Address Code

## 🧠 Problem Statement
This project constructs a Directed Acyclic Graph (DAG) from a list of Three-Address Code (TAC) instructions and visualizes it. The goal is to use a heuristic-based node ordering algorithm to find an optimal sequence for evaluating the expressions, ensuring operations are computed efficiently and dependencies are respected.

---

## 🔍 Problem Definition

This tool performs the following tasks:

- Parses a list of TAC (Three-Address Code) instructions.
- Constructs a DAG to represent computations and their dependencies.
- Applies a **heuristic-based node ordering** strategy for optimized evaluation.
- Eliminates redundant operations via subexpression elimination.
- Tracks variable reassignments during code generation.
- Visualizes the DAG to understand the flow of computations.

---

## 💡 Key Features

- **DAG Construction:** Automatically builds a directed acyclic graph from TAC input.
- **Subexpression Elimination:** Avoids duplicate computations by reusing existing nodes.
- **Heuristic Node Ordering:** Determines the most efficient sequence to evaluate operations based on dependencies.
- **DAG Visualization:** Graphical output that shows computation flow using `networkx` and `matplotlib`.

---

## 🧪 Technologies Used

- Python 3.x
- Flask
- NetworkX
- Matplotlib
- HTML/CSS/JavaScript (Frontend)
- Bootstrap (UI Styling)

---

## 📷 Screenshot

> Example DAG Visualization output and computation sequence (to be added).

---

## 👨‍💻 Team Members

1. Niraj Dhanore  
2. Mayank Wasu  
3. Jayesh Dhakate  

---

## 🚀 How to Run

```bash
# Clone the repository
git clone https://github.com/NirajD04/DAG_optimal.git
cd DAG_optimal

# Install dependencies (preferably in a virtual environment)
pip install -r requirements.txt

# Run the Flask app
python app.py
