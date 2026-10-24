import React from 'react';
import katex from 'katex';

/**
 * Safely renders LaTeX mathematical expressions with fallback.
 * Never throws or displays raw red error messages.
 */
function renderMath(latex, displayMode = false) {
  try {
    return (
      <span
        dangerouslySetInnerHTML={{
          __html: katex.renderToString(latex.trim(), {
            throwOnError: false,
            displayMode: displayMode,
          }),
        }}
      />
    );
  } catch (err) {
    // Graceful fallback: render clean text without raw LaTeX tags
    const cleaned = latex.replace(/\\text\{([^}]+)\}/g, '$1').replace(/\\times/g, '×');
    return <span className="formula-fallback">{cleaned}</span>;
  }
}

/**
 * Formats inline text with bold (**text**), citations, and inline math ($...$).
 */
function renderInline(text) {
  if (!text) return null;

  // Split by inline math delimiter ($...$)
  const mathParts = text.split(/(\$[^\$]+\$)/g);

  return mathParts.map((part, pIdx) => {
    if (part.startsWith('$') && part.endsWith('$') && part.length > 2) {
      const mathContent = part.slice(1, -1);
      return <React.Fragment key={pIdx}>{renderMath(mathContent, false)}</React.Fragment>;
    }

    // Split by bold (**...**)
    const boldParts = part.split(/(\*\*[^*]+\*\*)/g);
    return boldParts.map((bPart, bIdx) => {
      if (bPart.startsWith('**') && bPart.endsWith('**') && bPart.length > 4) {
        return (
          <strong key={`${pIdx}-${bIdx}`} style={{ color: 'var(--text-primary)', fontWeight: 700 }}>
            {bPart.slice(2, -2)}
          </strong>
        );
      }

      // Highlight source citations (Document Name, Page X)
      const citationRegex = /(\([^\)]+?,\s*Page\s*\d+\))/g;
      const citationParts = bPart.split(citationRegex);

      return citationParts.map((cPart, cIdx) => {
        if (citationRegex.test(cPart)) {
          return (
            <span
              key={`${pIdx}-${bIdx}-${cIdx}`}
              className="inline-citation"
              title="Official Document Citation"
            >
              {cPart}
            </span>
          );
        }
        return cPart;
      });
    });
  });
}

export default function FormattedContent({ content }) {
  if (!content) return null;

  // Split into lines/blocks
  const lines = content.split('\n');
  const elements = [];
  let currentList = [];

  const flushList = (key) => {
    if (currentList.length > 0) {
      elements.push(
        <ul key={key} className="formatted-list">
          {currentList.map((item, i) => (
            <li key={i}>{renderInline(item)}</li>
          ))}
        </ul>
      );
      currentList = [];
    }
  };

  lines.forEach((rawLine, idx) => {
    const line = rawLine.trim();

    // Check for display math block ($$...$$)
    if (line.startsWith('$$') && line.endsWith('$$') && line.length > 4) {
      flushList(`list-${idx}`);
      const latex = line.slice(2, -2);
      elements.push(
        <div key={`math-block-${idx}`} className="math-display-block">
          {renderMath(latex, true)}
        </div>
      );
      return;
    }

    // Check for headings
    if (line.startsWith('### ')) {
      flushList(`list-${idx}`);
      elements.push(
        <h4 key={`h3-${idx}`} className="formatted-h3">
          {renderInline(line.slice(4))}
        </h4>
      );
      return;
    }
    if (line.startsWith('## ')) {
      flushList(`list-${idx}`);
      elements.push(
        <h3 key={`h2-${idx}`} className="formatted-h2">
          {renderInline(line.slice(3))}
        </h3>
      );
      return;
    }
    if (line.startsWith('# ')) {
      flushList(`list-${idx}`);
      elements.push(
        <h2 key={`h1-${idx}`} className="formatted-h1">
          {renderInline(line.slice(2))}
        </h2>
      );
      return;
    }

    // Check for list items (* or - or numbered 1.)
    const listMatch = line.match(/^(\*|-|\d+\.)\s+(.+)$/);
    if (listMatch) {
      currentList.push(listMatch[2]);
      return;
    }

    // Check for blockquotes
    if (line.startsWith('> ')) {
      flushList(`list-${idx}`);
      elements.push(
        <blockquote key={`quote-${idx}`} className="formatted-quote">
          {renderInline(line.slice(2))}
        </blockquote>
      );
      return;
    }

    // Check for formula lines (e.g. "CGPA = ...", "SGPA = ...")
    if (line.includes(' = ') && (line.includes('CGPA') || line.includes('SGPA') || line.includes('Sum of'))) {
      flushList(`list-${idx}`);
      elements.push(
        <div key={`formula-${idx}`} className="formula-box">
          {renderInline(line)}
        </div>
      );
      return;
    }

    // Empty lines act as separators
    if (!line) {
      flushList(`list-${idx}`);
      return;
    }

    // Regular paragraphs
    flushList(`list-${idx}`);
    elements.push(
      <p key={`p-${idx}`} className="formatted-p">
        {renderInline(line)}
      </p>
    );
  });

  flushList('final-list');

  return <div className="formatted-content-root">{elements}</div>;
}
