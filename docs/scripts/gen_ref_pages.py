"""Generate the code reference pages and navigation."""

import sys
from pathlib import Path
from typing import List, Tuple
from urllib.parse import urlparse

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()
mod_symbol = '<code class="doc-symbol doc-symbol-nav doc-symbol-module"></code>'


def clean_docstring(docs: List[str]) -> str:
    summary = " ".join(docs[1:]).strip('"""').strip("'''")
    title = docs[0].strip('"""').strip("'''")
    return f"{title}<br><br>{summary}"


def read_class(file_path) -> Tuple[str, str, list]:
    with open(file_path, "r") as file:
        lines = file.readlines()

    inside_class = False
    inside_sources = False
    docstring_lines = []
    sources = []
    name = ""

    for line in lines:
        if line.strip().startswith("class"):
            name = line.strip().split("class")[-1].split("(")[0]
            inside_class = True

        if inside_class:
            if '"""' in line or "'''" in line:
                docstring_lines.append(line.strip())
                if len(docstring_lines) > 1:
                    break
            elif "Sources:" in line:
                inside_sources = True
            elif (inside_sources and not line.strip()) or "Output type:" in line:
                break
            elif inside_sources:
                sources.append(line.strip())
            elif docstring_lines:
                docstring_lines.append(line.strip())

    return (
        name,
        clean_docstring(docstring_lines),
        sources,
    )


def read_methods(file_path) -> List[Tuple[str, str, str]]:
    with open(file_path, "r") as file:
        lines = file.readlines()

    inside_method = False
    inside_desc = False
    methods = []
    docstring_lines = []
    name = ""
    source = ""

    for line in lines:
        if line.strip().startswith("def"):
            name = line.split("def")[-1].split("(")[0].strip()
            if not name.startswith("_"):
                inside_method = True

        if inside_method:
            if '"""' in line or "'''" in line:
                docstring_lines.append(line.strip())
                if len(docstring_lines) > 1:
                    break
            elif "Source:" in line:
                source = line.strip().split(" ")[-1]
            elif (inside_desc and not line.strip()) or "Args:" in line:
                methods.append((name, clean_docstring(docstring_lines), source))
                inside_method = False
                inside_desc = False
                docstring_lines = []
                source = ""
            elif docstring_lines:
                docstring_lines.append(line.strip())
    return methods


def generate_indicator_catalog(root):
    catalog_path = "indicator-catalogue.md"

    with mkdocs_gen_files.open(catalog_path, "w") as fd:
        fd.write("Indicator usage guide found at ")
        fd.write(
            "[Quick Start](guides/quick-start.md) Or  [In depth.](guides/indicators-indepth.md)\n\n"
        )
        fd.write("| Indicator | Description | Sources |\n")
        fd.write("| :---------- | :------ | :------ |\n")

    for path in sorted(Path(root, "hexital/indicators/").rglob("*.py")):
        module_path = path.relative_to(root)
        doc_path = path.relative_to(root).with_suffix(".md")
        full_doc_path = Path("reference", doc_path)
        parts = tuple(module_path.with_suffix("").parts)

        if parts[-1] in ["__main__", "amorph", "__init__"]:
            continue

        name, docstring, sources = read_class(module_path)

        with mkdocs_gen_files.open(catalog_path, "a") as fd:
            fd.write(f"|**[{name}]({full_doc_path})**|")
            fd.write(f"{docstring}|")
            for source in sources:
                fd.write(f"[{urlparse(source).netloc}]({source})<br>")
            fd.write("|\n")


def generate_pattern_catalog(root):
    catalog_path = "candle-pattern-catalogue.md"

    with mkdocs_gen_files.open(catalog_path, "w") as fd:
        fd.write("Candle Pattern's usage guide found at ")
        fd.write("[Analysis guide.](guides/analysis-indepth.md)\n\n")
        fd.write("| Pattern | Description | Source |\n")
        fd.write("| :---------- | :------ | :------ |\n")

    path = Path(root, "hexital/analysis/patterns.py")
    module_path = path.relative_to(root)
    doc_path = path.relative_to(root).with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    patterns = read_methods(module_path)

    with mkdocs_gen_files.open(catalog_path, "a") as fd:
        for pattern in patterns:
            fd.write(
                f"|**[{pattern[0]}]({full_doc_path}#hexital.analysis.patterns.{pattern[0]})**|"
            )
            fd.write(f"{pattern[1]}|")
            fd.write(f"[{urlparse(pattern[2]).netloc}]({pattern[2]})<br>")
            fd.write("|\n")


def generate_candlestick_catalog(root):
    catalog_path = "candlesticks-catalogue.md"

    with mkdocs_gen_files.open(catalog_path, "w") as fd:
        fd.write("Candlestick's usage guide found at ")
        fd.write("[Candlesticks guide.](guides/candlesticks.md)\n\n")
        fd.write("| Candlestick Type | Description | Sources |\n")
        fd.write("| :---------- | :------ | :------ |\n")

    for path in sorted(Path(root, "hexital/candlesticks/").rglob("*.py")):
        module_path = path.relative_to(root)
        doc_path = path.relative_to(root).with_suffix(".md")
        full_doc_path = Path("reference", doc_path)
        parts = tuple(module_path.with_suffix("").parts)

        if parts[-1] in ["__main__", "__init__"]:
            continue

        name, docstring, sources = read_class(module_path)

        with mkdocs_gen_files.open(catalog_path, "a") as fd:
            fd.write(f"|**[{name}]({full_doc_path})**|")
            fd.write(f"{docstring}|")
            for source in sources:
                fd.write(f"[{urlparse(source).netloc}]({source})<br>")
            fd.write("|\n")


def generate_api_reference(root):
    for path in sorted(Path(root, "hexital").rglob("*.py")):
        module_path = path.relative_to(root).with_suffix("")
        doc_path = path.relative_to(root).with_suffix(".md")
        full_doc_path = Path("reference", doc_path)

        parts = tuple(module_path.parts)

        if parts[-1] == "__init__":
            parts = parts[:-1]
            doc_path = doc_path.with_name("index.md")
            full_doc_path = full_doc_path.with_name("index.md")
        elif parts[-1] == "__main__":
            continue

        nav_parts = [f"{mod_symbol} {part}" for part in parts]
        nav[tuple(nav_parts)] = doc_path.as_posix()

        with mkdocs_gen_files.open(full_doc_path, "w") as fd:
            ident = ".".join(parts)
            fd.write(f"::: {ident}")

        mkdocs_gen_files.set_edit_path(full_doc_path, path.relative_to(root))

    with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
        nav_file.writelines(nav.build_literate_nav())


def main():
    root = Path(__file__).parent.parent.parent
    generate_api_reference(root)
    generate_indicator_catalog(root)
    generate_pattern_catalog(root)
    generate_candlestick_catalog(root)


sys.exit(main())
