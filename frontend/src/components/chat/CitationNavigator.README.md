# CitationNavigator Component

Navigation controls for browsing multiple citations in a message.

## Features

- Current index and total count display (e.g., "1 / 3")
- Previous/next navigation buttons with Material Design icons
- Disabled states at navigation boundaries
- Hover effects and smooth transitions
- Full keyboard accessibility support
- Focus management with visible focus rings

## Usage

```tsx
import { CitationNavigator } from '@/components/chat';

function ContextPanel() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const citations = [...]; // Array of citations
  
  const handleNext = () => {
    setCurrentIndex(prev => Math.min(prev + 1, citations.length - 1));
  };
  
  const handlePrevious = () => {
    setCurrentIndex(prev => Math.max(prev - 1, 0));
  };
  
  return (
    <div>
      <CitationNavigator
        currentIndex={currentIndex}
        totalCount={citations.length}
        onNext={handleNext}
        onPrevious={handlePrevious}
      />
      {/* Display current citation */}
    </div>
  );
}
```

## Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `currentIndex` | `number` | Yes | Current citation index (0-based) |
| `totalCount` | `number` | Yes | Total number of citations |
| `onNext` | `() => void` | Yes | Callback when next button is clicked |
| `onPrevious` | `() => void` | Yes | Callback when previous button is clicked |

## Behavior

### Navigation Boundaries

- **Previous button**: Disabled when `currentIndex === 0`
- **Next button**: Disabled when `currentIndex === totalCount - 1`

### Display Format

The counter displays as "X / Y" where:
- X = `currentIndex + 1` (1-based for user display)
- Y = `totalCount`

Examples:
- First citation: "1 / 3"
- Second citation: "2 / 3"
- Last citation: "3 / 3"

### Accessibility

- Both buttons have `aria-label` attributes for screen readers
- Disabled buttons have `disabled` attribute and visual styling
- Focus rings appear on keyboard navigation
- Buttons are keyboard accessible (Tab, Enter, Space)

## Styling

The component uses Material Design 3 theme tokens:

- **Background**: `bg-surface-container-low`
- **Border**: `border-outline-variant/10`
- **Text**: `text-text-primary`
- **Buttons**: `bg-surface-container` with hover state
- **Disabled**: Reduced opacity (50%) with `cursor-not-allowed`
- **Icons**: Material Symbols Outlined (`chevron_left`, `chevron_right`)

## Requirements

Validates: Requirements 1.8

## Related Components

- `ContextPanel` - Parent component that uses CitationNavigator
- `ContextPanelHeader` - Header component for the context panel
- `CodeDisplay` - Displays the citation content
