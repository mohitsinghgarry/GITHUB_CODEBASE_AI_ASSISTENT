/**
 * CodeDisplay Component Examples
 * 
 * This file demonstrates the CodeDisplay component with various use cases.
 * It can be used for manual testing and verification.
 */

import { CodeDisplay } from './CodeDisplay';

// Example 1: TypeScript code with line highlighting
export function TypeScriptExample() {
  const code = `function greet(name: string): string {
  return \`Hello, \${name}!\`;
}

const message = greet("World");
console.log(message);`;

  return (
    <div className="space-y-4 p-4">
      <h3 className="text-lg font-semibold">TypeScript Example</h3>
      <CodeDisplay
        content={code}
        language="typescript"
        startLine={1}
        endLine={3}
      />
    </div>
  );
}

// Example 2: Python code with single line highlight
export function PythonExample() {
  const code = `def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total

result = calculate_sum([1, 2, 3, 4, 5])
print(f"Sum: {result}")`;

  return (
    <div className="space-y-4 p-4">
      <h3 className="text-lg font-semibold">Python Example (Single Line)</h3>
      <CodeDisplay
        content={code}
        language="python"
        startLine={1}
        endLine={1}
      />
    </div>
  );
}

// Example 3: JavaScript code with middle lines highlighted
export function JavaScriptExample() {
  const code = `const users = [
  { id: 1, name: "Alice" },
  { id: 2, name: "Bob" },
  { id: 3, name: "Charlie" }
];

const activeUsers = users.filter(user => user.id > 1);
console.log(activeUsers);`;

  return (
    <div className="space-y-4 p-4">
      <h3 className="text-lg font-semibold">JavaScript Example</h3>
      <CodeDisplay
        content={code}
        language="javascript"
        startLine={1}
        endLine={5}
      />
    </div>
  );
}

// Example 4: Plain text (null language)
export function PlainTextExample() {
  const code = `This is plain text content.
No syntax highlighting should be applied.
Line numbers should still be visible.`;

  return (
    <div className="space-y-4 p-4">
      <h3 className="text-lg font-semibold">Plain Text Example (null language)</h3>
      <CodeDisplay
        content={code}
        language={null}
        startLine={10}
        endLine={12}
      />
    </div>
  );
}

// Example 5: Code starting at a higher line number
export function HighLineNumberExample() {
  const code = `    if (condition) {
        performAction();
    }
}`;

  return (
    <div className="space-y-4 p-4">
      <h3 className="text-lg font-semibold">High Line Number Example</h3>
      <CodeDisplay
        content={code}
        language="typescript"
        startLine={45}
        endLine={47}
      />
    </div>
  );
}

// Example 6: All examples together
export function AllExamples() {
  return (
    <div className="space-y-8 bg-surface p-8">
      <h2 className="text-2xl font-bold">CodeDisplay Component Examples</h2>
      <TypeScriptExample />
      <PythonExample />
      <JavaScriptExample />
      <PlainTextExample />
      <HighLineNumberExample />
    </div>
  );
}
