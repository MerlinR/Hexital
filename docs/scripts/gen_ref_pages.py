"""Generate the code reference pages and navigation. This code is trash, Please dont read this."""

import sys
from pathlib import Path
from typing import List, Tuple
from urllib.parse import urlparse

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()
mod_symbol = '<code class="doc-symbol doc-symbol-nav doc-symbol-module"></code>'


def clean_docstring(docs: List[str]) -> Tuple[str, str]:
    if not docs:
        return "", ""

    summary = " ".join(docs[1:]).strip('"""').strip("'''")
    title = docs[0].strip('"""').strip("'''")

    return title, f"**{title}**<br><br>{summary}"


def write_table(path, intro, headers, rows):
    with mkdocs_gen_files.open(path, "w") as fd:
        fd.write(intro + "\n\n")
        fd.write("|" + "|".join(headers) + "|\n")
        fd.write("|" + "".join([":------|" for _ in range(len(headers))]) + "\n")

        for row in rows:
            for field in row:
                fd.write(f"| {field} ")
            fd.write("|")
            fd.write("\n")


def read_class(file_path) -> Tuple[str, str, str, list]:
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

    title, docstring = clean_docstring(docstring_lines)

    return (
        name,
        title.strip(),
        docstring,
        sources,
    )


def read_methods(file_path) -> List[Tuple[str, str, str, str]]:
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
                title, docstring = clean_docstring(docstring_lines)
                methods.append((name, title, docstring, source))
                inside_method = False
                inside_desc = False
                docstring_lines = []
                source = ""
            elif docstring_lines:
                docstring_lines.append(line.strip())
    return methods


def generate_indicator_catalog(root):
    catalog_path = "indicator-catalogue.md"

    intro = "Indicator usage guide found at [Quick Start](guides/quick-start.md) Or  [In depth.](guides/indicators-indepth.md)"
    table_headers = ["Indicator", "API", "Description", "Sources"]
    rows = []

    for path in sorted(Path(root, "hexital/indicators/").rglob("*.py")):
        module_path = path.relative_to(root)
        full_doc_path = Path("reference", path.relative_to(root).with_suffix(".md"))
        parts = tuple(module_path.with_suffix("").parts)

        if parts[-1] in ["__main__", "amorph", "__init__"]:
            continue

        name, title, docstring, sources = read_class(module_path)

        rows.append(
            [
                f"**{title}**",
                f"*[{name}]({full_doc_path})*",
                f"{docstring}",
                "<br>".join([f"[{urlparse(source).netloc}]({source})" for source in sources]),
            ]
        )

    write_table(catalog_path, intro, table_headers, rows)


def generate_pattern_catalog(root):
    catalog_path = "candle-pattern-catalogue.md"

    intro = "Candle Pattern's usage guide found at [Analysis guide.](guides/analysis-indepth.md)"
    table_headers = ["Pattern", "API", "Description", "Source"]
    rows = []

    path = Path(root, "hexital/analysis/patterns.py")
    full_doc_path = Path("reference", path.relative_to(root).with_suffix(".md"))

    for pattern in read_methods(path.relative_to(root)):
        rows.append(
            [
                f"**{pattern[1].split("Pattern")[0].strip()}**",
                f"*[{pattern[0]}]({full_doc_path}#hexital.analysis.patterns.{pattern[0]})*",
                f"{pattern[2]}",
                f"[{urlparse(pattern[3]).netloc}]({pattern[3]})<br>",
            ]
        )

    write_table(catalog_path, intro, table_headers, rows)


def generate_analysis_catalog(root):
    catalog_path = "analysis-catalogue.md"
    intro = "Candle analysis usage guide found at [Analysis guide.](guides/analysis-indepth.md)"
    table_headers = ["Pattern", "API", "Description"]
    rows = []

    path = Path(root, "hexital/analysis/movement.py")
    full_doc_path = Path("reference", path.relative_to(root).with_suffix(".md"))

    for pattern in read_methods(path.relative_to(root)):
        rows.append(
            [
                f"**{pattern[1].split("Analysis")[0].strip()}**",
                f"*[{pattern[0]}]({full_doc_path}#hexital.analysis.movement.{pattern[0]})*",
                f"{pattern[2]}",
            ]
        )

    write_table(catalog_path, intro, table_headers, rows)


def generate_candlestick_catalog(root):
    catalog_path = "candlesticks-catalogue.md"

    intro = "Candlestick's usage guide found at [Candlesticks guide.](guides/candlesticks.md)"
    table_headers = ["Candlestick Type", "API", "Description", "Sources"]
    rows = []

    for path in sorted(Path(root, "hexital/candlesticks/").rglob("*.py")):
        module_path = path.relative_to(root)
        full_doc_path = Path("reference", path.relative_to(root).with_suffix(".md"))
        parts = tuple(module_path.with_suffix("").parts)

        if parts[-1] in ["__main__", "__init__"]:
            continue

        name, title, docstring, sources = read_class(module_path)

        rows.append(
            [
                f"**{title}**",
                f"*[{name}]({full_doc_path})*",
                f"{docstring}",
                "<br>".join([f"[{urlparse(source).netloc}]({source})" for source in sources]),
            ]
        )

    write_table(catalog_path, intro, table_headers, rows)


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
    generate_analysis_catalog(root)


sys.exit(main())
