#!/usr/bin/env python3
"""Build README.md files from template.

Generates two versions:
- README.md: For GitHub (relative paths)
- README_PYPI.md: For PyPI (absolute GitHub URLs)
"""

from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
TEMPLATE_FILE = PROJECT_DIR / 'docs' / 'README_template.md'

GITHUB_RAW_PREFIX = 'https://raw.githubusercontent.com/Alyxion/nice-vibes/main/'
GITHUB_TREE_PREFIX = 'https://github.com/Alyxion/nice-vibes/tree/main/'
GITHUB_BLOB_PREFIX = 'https://github.com/Alyxion/nice-vibes/blob/main/'


def build_readme(template: str, for_pypi: bool = False) -> str:
    """Build README content from template.
    
    :param template: Template content
    :param for_pypi: If True, use absolute GitHub URLs; otherwise relative paths
    :return: Processed README content
    """
    if for_pypi:
        # PyPI version: absolute URLs
        content = template.replace('{{ASSETS_PREFIX}}', GITHUB_RAW_PREFIX)
        content = content.replace('{{GITHUB_PREFIX}}', GITHUB_BLOB_PREFIX)
        content = content.replace('{{DOCS_PREFIX}}', GITHUB_TREE_PREFIX)
        content = content.replace('{{DOCS_SUFFIX}}', '')
        content = content.replace('{{SHOWCASE_WIDTH}}', ' width="600"')
    else:
        # GitHub version: relative paths
        content = template.replace('{{ASSETS_PREFIX}}', '')
        content = content.replace('{{GITHUB_PREFIX}}', '')
        content = content.replace('{{DOCS_PREFIX}}', '')
        content = content.replace('{{DOCS_SUFFIX}}', '/')
        content = content.replace('{{SHOWCASE_WIDTH}}', '')
    
    return content


def main():
    """Build both README versions."""
    if not TEMPLATE_FILE.exists():
        print(f'Error: Template not found at {TEMPLATE_FILE}')
        return 1
    
    template = TEMPLATE_FILE.read_text()
    
    # Build GitHub README
    readme_content = build_readme(template, for_pypi=False)
    readme_file = PROJECT_DIR / 'README.md'
    readme_file.write_text(readme_content)
    print(f'Generated {readme_file}')
    
    # Build PyPI README
    pypi_content = build_readme(template, for_pypi=True)
    pypi_file = PROJECT_DIR / 'README_PYPI.md'
    pypi_file.write_text(pypi_content)
    print(f'Generated {pypi_file}')
    
    return 0


if __name__ == '__main__':
    exit(main())
