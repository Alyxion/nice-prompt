#!/usr/bin/env python3
"""
Build the samples README gallery from template and sample READMEs.

Usage:
    poetry run python scripts/build_samples_gallery.py
"""
import re
from pathlib import Path


SAMPLES_DIR = Path(__file__).parent.parent / 'samples'
TEMPLATE_FILE = SAMPLES_DIR / 'README_template.md'
OUTPUT_FILE = SAMPLES_DIR / 'README.md'


def discover_samples() -> list[tuple[str, str, str]]:
    """Discover samples by reading their README files.
    
    Returns list of (name, title, description) tuples.
    """
    samples = []
    
    for sample_dir in sorted(SAMPLES_DIR.iterdir()):
        if not sample_dir.is_dir():
            continue
        
        readme = sample_dir / 'README.md'
        screenshot = sample_dir / 'screenshot.jpg'
        main_py = sample_dir / 'main.py'
        
        # Must have main.py and screenshot
        if not main_py.exists() or not screenshot.exists():
            continue
        
        # Parse README for title and description
        if readme.exists():
            content = readme.read_text()
            lines = content.strip().split('\n')
            
            # Title is first H1
            title = sample_dir.name.replace('_', ' ').title()
            for line in lines:
                if line.startswith('# '):
                    title = line[2:].strip()
                    break
            
            # Description is first non-empty line after title (skip screenshot and HTML comments)
            description = ''
            found_title = False
            for line in lines:
                if line.startswith('# '):
                    found_title = True
                    continue
                stripped = line.strip()
                if found_title and stripped and not stripped.startswith('![') and not stripped.startswith('<!--'):
                    description = stripped
                    break
        else:
            title = sample_dir.name.replace('_', ' ').title()
            description = ''
        
        samples.append((sample_dir.name, title, description))
    
    return samples


def is_animated(sample_name: str) -> bool:
    """Check if sample has an animated GIF."""
    animated_gif = SAMPLES_DIR / sample_name / 'animated.gif'
    return animated_gif.exists()


def build_gallery() -> str:
    """Build the gallery as HTML with 3-column layout."""
    samples = discover_samples()
    items = []
    
    for name, title, description in samples:
        # Use animated.gif if available, otherwise screenshot.jpg
        if is_animated(name):
            img_src = f'{name}/animated.gif'
        else:
            img_src = f'{name}/screenshot.jpg'
        
        # Use fixed height for title to ensure image alignment
        items.append(f'''<td align="center" valign="top" width="33%">
<div style="height: 40px; display: flex; align-items: center; justify-content: center;">
<a href="{name}/"><strong>{title}</strong></a>
</div>
<a href="{name}/"><img src="{img_src}" width="280"></a><br>
<sub>{description}</sub>
</td>''')
    
    # Build rows of 3
    rows = []
    for i in range(0, len(items), 3):
        row_items = items[i:i+3]
        # Pad with empty cells if needed
        while len(row_items) < 3:
            row_items.append('<td></td>')
        rows.append('<tr>\n' + '\n'.join(row_items) + '\n</tr>')
    
    return '<table>\n' + '\n'.join(rows) + '\n</table>'


def main():
    print('Building samples gallery...')
    
    # Read template
    template = TEMPLATE_FILE.read_text()
    
    # Build gallery
    gallery = build_gallery()
    
    # Replace placeholder
    output = re.sub(
        r'<!-- GALLERY_START -->.*<!-- GALLERY_END -->',
        f'<!-- GALLERY_START -->\n{gallery}<!-- GALLERY_END -->',
        template,
        flags=re.DOTALL,
    )
    
    # Write output
    OUTPUT_FILE.write_text(output)
    print(f'  Saved: {OUTPUT_FILE}')
    
    # Also build the showcase GIF
    from build_samples_gif import build_gif
    build_gif()


if __name__ == '__main__':
    main()
