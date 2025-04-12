from flask import Flask, render_template, request, jsonify
import networkx as nx
import matplotlib.pyplot as plt
import io
import base64
import json
import traceback

app = Flask(__name__)

# Your existing DAG code
nodes = []
label_to_node_index = {}

def create_node(op, left_index, right_index):
    node = {
        "op": op,
        "left": left_index,
        "right": right_index,
        "labels": []
    }
    nodes.append(node)
    return len(nodes) - 1

def find_node(op, left_index, right_index):
    for idx, n in enumerate(nodes):
        if n["op"] == op and n["left"] == left_index and n["right"] == right_index:
            return idx
    return None

def ensure_node_for_label(label):
    if label not in label_to_node_index:
        idx = create_node(op=None, left_index=None, right_index=None)
        nodes[idx]["labels"].append(label)
        label_to_node_index[label] = idx
    return label_to_node_index[label]

def attach_label_to_node(label, node_index):
    if label in label_to_node_index:
        old_idx = label_to_node_index[label]
        if old_idx != node_index and label in nodes[old_idx]["labels"]:
            nodes[old_idx]["labels"].remove(label)
    if label not in nodes[node_index]["labels"]:
        nodes[node_index]["labels"].append(label)
    label_to_node_index[label] = node_index

def parse_instruction(instr):
    try:
        left, right = instr.split(":=")
        x = left.strip()
        right = right.strip()

        if "[" in right and "]" in right:
            array_name, inside = right.split("[")
            array_name = array_name.strip()
            inside = inside.replace("]", "").strip()
            return (x, "[]", array_name, inside)

        parts = right.split()
        if len(parts) == 3:
            y, op, z = parts
            return (x, op, y, z)
        elif len(parts) == 2:
            op, y = parts
            return (x, op, y, None)
        else:
            return (x, None, right, None)
    except Exception as e:
        raise ValueError(f"Error parsing instruction: {instr}. Error: {str(e)}")

def process_instruction(x, op, y, z):
    try:
        y_index = ensure_node_for_label(y) if y is not None else None
        z_index = ensure_node_for_label(z) if z is not None else None

        if op is None:
            n_index = y_index
        elif op == "[]":
            existing = find_node(op, y_index, z_index)
            n_index = existing if existing is not None else create_node(op, y_index, z_index)
        else:
            if z is None:
                existing = find_node(op, y_index, None)
                n_index = existing if existing is not None else create_node(op, y_index, None)
            else:
                existing = find_node(op, y_index, z_index)
                n_index = existing if existing is not None else create_node(op, y_index, z_index)

        attach_label_to_node(x, n_index)
    except Exception as e:
        raise ValueError(f"Error processing instruction: {x} := {y} {op} {z}. Error: {str(e)}")

def construct_dag_from_instructions(instructions):
    global nodes, label_to_node_index
    nodes = []
    label_to_node_index = {}
    for instr in instructions:
        try:
            x, op, y, z = parse_instruction(instr)
            process_instruction(x, op, y, z)
        except Exception as e:
            raise ValueError(f"Error in instruction: {instr}. {str(e)}")
    return nodes

def node_listing():
    try:
        num_nodes = len(nodes)
        parents = {i: [] for i in range(num_nodes)}
        for i, node in enumerate(nodes):
            if node["left"] is not None:
                parents[node["left"]].append(i)
            if node["right"] is not None:
                parents[node["right"]].append(i)

        interior_nodes = {i for i, node in enumerate(nodes) if node["op"] is not None}
        listed = set()
        order = []

        def parents_listed(i):
            return all(p in listed for p in parents[i])

        while interior_nodes - listed:
            n = None
            for i in interior_nodes - listed:
                if parents_listed(i):
                    n = i
                    break
            if n is None:
                break
            order.append(n)
            listed.add(n)
            m = nodes[n]["left"]
            while m is not None and nodes[m]["op"] is not None and m not in listed and parents_listed(m):
                order.append(m)
                listed.add(m)
                n = m
                m = nodes[n]["left"]
        return order
    except Exception as e:
        raise ValueError(f"Error in node listing: {str(e)}")

def hierarchical_layout(G):
    try:
        levels = {}
        for node in nx.topological_sort(G):
            if G.in_degree(node) == 0:
                levels[node] = 0
            else:
                levels[node] = max(levels[p] for p in G.predecessors(node)) + 1

        level_nodes = {}
        for node, level in levels.items():
            level_nodes.setdefault(level, []).append(node)

        pos = {}
        for level, nodes in level_nodes.items():
            num_nodes = len(nodes)
            x_spacing = 1.0 / (num_nodes + 1)
            for i, node in enumerate(sorted(nodes)):
                pos[node] = ((i + 1) * x_spacing, -level)
        return pos
    except Exception as e:
        raise ValueError(f"Error in hierarchical layout: {str(e)}")

def visualize_dag(nodes):
    try:
        G = nx.DiGraph()
        for idx, node in enumerate(nodes):
            label = (f"{node['op']}\n({', '.join(node['labels'])})"
                    if node["op"] is not None else ", ".join(node["labels"]))
            G.add_node(idx, label=label)
        for idx, node in enumerate(nodes):
            if node["left"] is not None:
                G.add_edge(idx, node["left"])
            if node["right"] is not None:
                G.add_edge(idx, node["right"])

        pos = hierarchical_layout(G)
        labels = nx.get_node_attributes(G, 'label')
        
        plt.figure(figsize=(12, 8))
        nx.draw(G, pos, labels=labels, node_color='lightblue', node_size=2000,
                font_size=10, arrows=True, with_labels=True)
        plt.title("Hierarchical DAG Visualization")
        
        # Save the plot to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        buf.seek(0)
        plt.close()
        
        # Convert the buffer to base64
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        return image_base64
    except Exception as e:
        raise ValueError(f"Error in visualization: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    try:
        if not request.json or 'instructions' not in request.json:
            return jsonify({'error': 'No instructions provided'}), 400

        instructions = request.json['instructions']
        if not instructions.strip():
            return jsonify({'error': 'Instructions cannot be empty'}), 400

        instructions = [line.strip() for line in instructions.split('\n') if line.strip()]
        
        dag = construct_dag_from_instructions(instructions)
        image_base64 = visualize_dag(dag)
        
        ordering = node_listing()
        sequence = []
        for node_idx in ordering:
            node = nodes[node_idx]
            sequence.append(node['labels'])
        sequence = sequence[::-1]
        
        return jsonify({
            'image': image_base64,
            'sequence': sequence,
            'nodes': dag
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
