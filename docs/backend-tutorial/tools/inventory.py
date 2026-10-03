"""Inventory project-owned backend functions without importing the application."""

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "docs/backend-tutorial/inventory.json"


def python_file(path):
    source = path.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(path))
    functions = []
    classes = []

    class Visitor(ast.NodeVisitor):
        def __init__(self):
            self.owners = []

        def visit_ClassDef(self, node):
            classes.append({
                "name": ".".join([*self.owners, node.name]), "line": node.lineno,
                "bases": [ast.unparse(base) for base in node.bases],
                "doc": ast.get_docstring(node) or "",
            })
            self.owners.append(node.name)
            self.generic_visit(node)
            self.owners.pop()

        def visit_function(self, node):
            name = f"<lambda@{node.lineno}:{node.col_offset}>" if isinstance(node, ast.Lambda) else node.name
            calls = []

            class Calls(ast.NodeVisitor):
                def visit_Call(self, call):
                    calls.append(ast.unparse(call.func))
                    self.generic_visit(call)

                def visit_FunctionDef(self, child):
                    if child is node:
                        self.generic_visit(child)

                visit_AsyncFunctionDef = visit_FunctionDef

                def visit_Lambda(self, child):
                    if child is node:
                        self.generic_visit(child)

            Calls().visit(node)
            functions.append({
                "name": name,
                "qualname": ".".join([*self.owners, name]),
                "line": node.lineno, "end_line": node.end_lineno,
                "anonymous": isinstance(node, ast.Lambda),
                "params": ast.unparse(node.args),
                "doc": "" if isinstance(node, ast.Lambda) else ast.get_docstring(node) or "",
                "calls": list(dict.fromkeys(calls)),
                "source": ast.get_source_segment(source, node),
                "decorators": [] if isinstance(node, ast.Lambda) else [
                    ast.unparse(decorator) for decorator in node.decorator_list
                ],
            })
            self.owners.append(name)
            self.generic_visit(node)
            self.owners.pop()

        visit_FunctionDef = visit_function
        visit_AsyncFunctionDef = visit_function
        visit_Lambda = visit_function

    Visitor().visit(tree)
    return {"path": path.relative_to(ROOT).as_posix(), "functions": functions, "classes": classes}


def collect():
    paths = [ROOT / "main.py", ROOT / "alembic/env.py"]
    for directory in ["app", "tests", "alembic/versions"]:
        paths.extend((ROOT / directory).rglob("*.py"))
    files = [python_file(path) for path in sorted(paths) if "__pycache__" not in path.parts]
    for file in files:
        file["sha256"] = hashlib.sha256((ROOT / file["path"]).read_bytes()).hexdigest()
        for position, function in enumerate(file["functions"], 1):
            function["id"] = f"{file['path']}::{function['qualname']}:{function['line']}:{position}"
    data = {
        "scope": ["main.py", "app/**/*.py", "tests/**/*.py", "alembic/env.py", "alembic/versions/*.py"],
        "excluded": ["frontend", "dependencies", "generated files", "documentation tooling",
                     "alembic template not yet instantiated"],
        "files": files,
    }
    return data


def main():
    data = collect()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    files = data["files"]
    functions = [function for file in files for function in file["functions"]]
    print(json.dumps({
        "files": len(files), "functions": len(functions),
        "named": sum(not function["anonymous"] for function in functions),
        "lambdas": sum(function["anonymous"] for function in functions),
    }))


if __name__ == "__main__":
    main()
