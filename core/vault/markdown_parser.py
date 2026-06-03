"""Парсер Markdown → HTML для предпросмотра заметок."""

import html
import re

import markdown

from core.vault.mermaid_util import (
    MERMAID_FENCE_RE,
    extract_mermaid_source,
    is_standalone_mermaid_file,
)

MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"


class MermaidExtension(markdown.Extension):
    """Блоки ```mermaid → <pre class=\"mermaid\"> для mermaid.js."""

    def extendMarkdown(self, md: markdown.Markdown) -> None:
        md.preprocessors.register(MermaidPreprocessor(md), "mermaid", 175)


class MermaidPreprocessor(markdown.preprocessors.Preprocessor):
    """Заменяет fenced mermaid на элементы для клиентского рендеринга."""

    def run(self, lines: list[str]) -> list[str]:
        text = "\n".join(lines)

        def _replace(match: re.Match) -> str:
            code = html.escape(match.group(1).strip())
            return f'<pre class="mermaid">{code}</pre>'

        text = MERMAID_FENCE_RE.sub(_replace, text)
        return text.split("\n")


class MarkdownParser:
    """Конвертация Markdown в HTML с расширениями."""

    def __init__(self) -> None:
        self._extensions = [
            "fenced_code",
            "codehilite",
            "tables",
            "toc",
            "nl2br",
            "sane_lists",
            MermaidExtension(),
        ]
        self._extension_configs = {
            "codehilite": {"css_class": "highlight"},
        }

    def to_html(self, text: str) -> str:
        """Преобразовать Markdown-строку в HTML (тело документа)."""
        return markdown.markdown(
            text,
            extensions=self._extensions,
            extension_configs=self._extension_configs,
        )

    def build_preview_document(
        self,
        text: str,
        *,
        dark: bool = False,
        path: str = "",
    ) -> str:
        """HTML-документ с mermaid.js для QTextBrowser / QWebEngine."""
        lower = path.lower()
        if is_standalone_mermaid_file(path):
            body = f'<pre class="mermaid">{html.escape(text.strip())}</pre>'
        elif lower.endswith(".mermaid.md"):
            src = extract_mermaid_source(text, path)
            if src and "```" not in text:
                body = f'<pre class="mermaid">{html.escape(src)}</pre>'
            else:
                body = self.to_html(text)
        else:
            body = self.to_html(text)

        return _wrap_html_document(body, dark=dark)

    def get_preview_html(self, text: str, path: str = "") -> str:
        return self.build_preview_document(text, dark=False, path=path)

    def get_preview_html_dark(self, text: str, path: str = "") -> str:
        return self.build_preview_document(text, dark=True, path=path)


def _wrap_html_document(body: str, *, dark: bool) -> str:
    bg = "#000000" if dark else "#ffffff"
    fg = "#ffffff" if dark else "#000000"
    mermaid_theme = "dark" if dark else "default"
    link = "#64b5f6" if dark else "#1565c0"
    code_bg = "#1a1a1a" if dark else "#f5f5f5"
    border = "#333333" if dark else "#e0e0e0"

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="{MERMAID_CDN}"></script>
<style>
html, body {{
  margin: 0; padding: 16px;
  font-family: -apple-system, 'Segoe UI', sans-serif;
  line-height: 1.6;
  background: {bg}; color: {fg};
}}
pre:not(.mermaid) {{
  background: {code_bg}; padding: 12px; border-radius: 4px; overflow-x: auto;
}}
code {{ background: {code_bg}; padding: 2px 4px; border-radius: 3px; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid {border}; padding: 8px; text-align: left; }}
blockquote {{
  border-left: 3px solid {border}; margin: 0; padding-left: 12px; opacity: 0.85;
}}
img {{ max-width: 100%; }}
a {{ color: {link}; }}
h1, h2, h3, h4, h5, h6 {{ margin-top: 16px; margin-bottom: 8px; }}
hr {{ border: none; border-top: 1px solid {border}; margin: 16px 0; }}
.mermaid-wrap {{
  display: flex; justify-content: center; align-items: flex-start;
  min-height: 120px; overflow: hidden; cursor: grab;
}}
.mermaid-wrap:active {{ cursor: grabbing; }}
.mermaid-wrap svg {{ max-width: none; }}
</style>
</head>
<body>
{body}
<script>
(function() {{
  const dark = {str(dark).lower()};
  mermaid.initialize({{
    startOnLoad: false,
    theme: '{mermaid_theme}',
    securityLevel: 'loose',
    flowchart: {{ useMaxWidth: false }},
  }});

  function wrapMermaidNodes() {{
    document.querySelectorAll('pre.mermaid').forEach(function(pre) {{
      if (pre.parentElement && pre.parentElement.classList.contains('mermaid-wrap'))
        return;
      const wrap = document.createElement('div');
      wrap.className = 'mermaid-wrap';
      pre.parentNode.insertBefore(wrap, pre);
      wrap.appendChild(pre);
    }});
  }}

  wrapMermaidNodes();

  mermaid.run({{ nodes: document.querySelectorAll('.mermaid') }}).then(function() {{
    document.querySelectorAll('.mermaid-wrap svg').forEach(function(svg) {{
      let scale = 1;
      let panX = 0, panY = 0;
      let dragging = false;
      let lastX = 0, lastY = 0;
      const wrap = svg.closest('.mermaid-wrap');
      if (!wrap) return;

      function applyTransform() {{
        svg.style.transform = 'translate(' + panX + 'px,' + panY + 'px) scale(' + scale + ')';
        svg.style.transformOrigin = '0 0';
      }}

      wrap.addEventListener('wheel', function(e) {{
        e.preventDefault();
        const delta = e.deltaY > 0 ? 0.9 : 1.1;
        scale = Math.min(4, Math.max(0.2, scale * delta));
        applyTransform();
      }}, {{ passive: false }});

      wrap.addEventListener('mousedown', function(e) {{
        dragging = true;
        lastX = e.clientX;
        lastY = e.clientY;
      }});
      window.addEventListener('mousemove', function(e) {{
        if (!dragging) return;
        panX += e.clientX - lastX;
        panY += e.clientY - lastY;
        lastX = e.clientX;
        lastY = e.clientY;
        applyTransform();
      }});
      window.addEventListener('mouseup', function() {{ dragging = false; }});
      wrap.addEventListener('dblclick', function() {{
        scale = 1; panX = 0; panY = 0;
        applyTransform();
      }});
    }});
  }}).catch(function(err) {{
    console.error(err);
  }});
}})();
</script>
</body>
</html>"""
