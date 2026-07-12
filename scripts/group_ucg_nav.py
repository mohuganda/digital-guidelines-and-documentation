from pathlib import Path
import re
import sys

try:
    import yaml
except ImportError:
    print("PyYAML is not installed. Run: pip install pyyaml")
    sys.exit(1)

mkdocs_path = Path("mkdocs.yml")
backup_path = Path("mkdocs.yml.bak-before-auto-grouping-numbered-nav-v2")

original_text = mkdocs_path.read_text(encoding="utf-8")
config = yaml.safe_load(original_text)
backup_path.write_text(original_text, encoding="utf-8")

number_re = re.compile(r"^(\d+(?:\.\d+)+)\s+")

def get_number(label):
    match = number_re.match(str(label))
    return match.group(1) if match else None

def parent_numbers(num):
    parts = num.split(".")
    parents = []
    for i in range(len(parts) - 1, 1, -1):
        parents.append(".".join(parts[:i]))
    return parents

class Node:
    def __init__(self, label, path=None, children=None, raw=None):
        self.label = label
        self.path = path
        self.children = children or []
        self.raw = raw

def normalize_item(item):
    if isinstance(item, Node):
        return item

    if isinstance(item, str):
        return Node(label=item, path=item)

    if isinstance(item, dict):
        if len(item) != 1:
            return Node(label="UNSUPPORTED", raw=item)

        label, value = next(iter(item.items()))

        if isinstance(value, str):
            return Node(label=label, path=value)

        if isinstance(value, list):
            children = [normalize_item(child) for child in value]
            return Node(label=label, children=children)

    return Node(label="UNSUPPORTED", raw=item)

def node_to_yaml_item(node):
    node = normalize_item(node)

    if node.raw is not None:
        return node.raw

    if isinstance(node.label, str) and node.path == node.label and not node.children:
        return node.path

    if node.path and not node.children:
        return {node.label: node.path}

    if node.path and node.children:
        children = [{"Overview": node.path}]
        children.extend(node_to_yaml_item(child) for child in node.children)
        return {node.label: children}

    if node.children:
        return {node.label: [node_to_yaml_item(child) for child in node.children]}

    return {node.label: node.path or ""}

def flatten_existing_numbered_groups(children):
    flat = []

    for item in children:
        node = normalize_item(item)
        num = get_number(node.label)

        if num:
            flat.append(node)

            for child in node.children:
                child = normalize_item(child)

                if child.label == "Overview" and child.path and not node.path:
                    node.path = child.path
                    continue

                flat.append(child)

            node.children = []
        else:
            flat.append(node)

    return flat

def group_chapter_children(children):
    if not isinstance(children, list):
        return children

    children = [normalize_item(x) for x in children]
    children = flatten_existing_numbered_groups(children)

    fixed = []
    numbered_nodes = []
    by_number = {}

    for node in children:
        if isinstance(node.label, str) and node.path == node.label and node.label.endswith("/index.md"):
            fixed.append(node)
            continue

        num = get_number(node.label)

        if not num:
            fixed.append(node)
            continue

        numbered_nodes.append((num, node))
        by_number[num] = node

    attached = set()

    for num, node in numbered_nodes:
        for parent_num in parent_numbers(num):
            parent = by_number.get(parent_num)
            if parent is not None and parent is not node:
                parent.children.append(node)
                attached.add(num)
                break

    for num, node in numbered_nodes:
        if num not in attached:
            fixed.append(node)

    return [node_to_yaml_item(node) for node in fixed]

def process_nav_items(items):
    if not isinstance(items, list):
        return items

    new_items = []

    for item in items:
        if not isinstance(item, dict) or len(item) != 1:
            new_items.append(item)
            continue

        label, value = next(iter(item.items()))

        if label == "UCG 2023" and isinstance(value, list):
            new_ucg = []

            for chapter_item in value:
                if not isinstance(chapter_item, dict) or len(chapter_item) != 1:
                    new_ucg.append(chapter_item)
                    continue

                chapter_label, chapter_children = next(iter(chapter_item.items()))

                if isinstance(chapter_children, list):
                    new_ucg.append({chapter_label: group_chapter_children(chapter_children)})
                else:
                    new_ucg.append(chapter_item)

            new_items.append({label: new_ucg})
        else:
            new_items.append(item)

    return new_items

config["nav"] = process_nav_items(config.get("nav", []))

mkdocs_path.write_text(
    yaml.safe_dump(
        config,
        sort_keys=False,
        allow_unicode=True,
        width=140,
        default_flow_style=False
    ),
    encoding="utf-8"
)

print(f"Backup saved as: {backup_path}")
print("Updated mkdocs.yml by grouping numbered UCG sections.")
