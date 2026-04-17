import React from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { javascript } from '@codemirror/lang-javascript';
import { python } from '@codemirror/lang-python';
import { rust } from '@codemirror/lang-rust';
import { java } from '@codemirror/lang-java';
import { cpp } from '@codemirror/lang-cpp';
import { php } from '@codemirror/lang-php';
import { oneDark } from '@codemirror/theme-one-dark';
import { EditorView } from '@codemirror/view';

interface CodeDisplayProps {
  content: string;
  language: string | null;
  startLine: number;
  endLine: number;
}

// Get CodeMirror language extension based on language string
const getLanguageExtension = (language: string | null) => {
  if (!language) return javascript();
  
  switch (language.toLowerCase()) {
    case 'javascript':
    case 'js':
    case 'jsx':
      return javascript({ jsx: true });
    case 'typescript':
    case 'ts':
    case 'tsx':
      return javascript({ jsx: true, typescript: true });
    case 'python':
    case 'py':
      return python();
    case 'rust':
    case 'rs':
      return rust();
    case 'java':
      return java();
    case 'cpp':
    case 'c++':
    case 'c':
      return cpp();
    case 'php':
      return php();
    default:
      return javascript();
  }
};

/**
 * CodeDisplay component renders code with syntax highlighting, line numbers,
 * and highlighted line ranges using CodeMirror.
 *
 * **Validates: Requirements 1.3, 1.4, 1.5**
 */
export function CodeDisplay({
  content,
  language,
  startLine,
  endLine,
}: CodeDisplayProps): JSX.Element {
  return (
    <div className="overflow-x-auto rounded-lg border border-white/10">
      <CodeMirror
        value={content}
        extensions={[getLanguageExtension(language), EditorView.lineWrapping]}
        theme={oneDark}
        editable={false}
        readOnly={true}
        basicSetup={{
          lineNumbers: true,
          highlightActiveLineGutter: false,
          highlightSpecialChars: true,
          foldGutter: false,
          drawSelection: false,
          dropCursor: false,
          allowMultipleSelections: false,
          indentOnInput: false,
          syntaxHighlighting: true,
          bracketMatching: true,
          closeBrackets: false,
          autocompletion: false,
          rectangularSelection: false,
          crosshairCursor: false,
          highlightActiveLine: false,
          highlightSelectionMatches: false,
          closeBracketsKeymap: false,
          searchKeymap: true,
          foldKeymap: false,
          completionKeymap: false,
          lintKeymap: false,
        }}
        style={{
          fontSize: '14px',
          backgroundColor: '#000000',
        }}
        className="[&_.cm-editor]:!bg-[#000000] [&_.cm-gutters]:!bg-[#000000] [&_.cm-scroller]:!bg-[#000000] [&_.cm-content]:!bg-[#000000]"
      />
    </div>
  );
}
