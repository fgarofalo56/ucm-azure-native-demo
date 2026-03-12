---
applyTo:
  - "**/src/components/**"
  - "**/src/pages/**"
  - "**/src/views/**"
  - "**/src/app/**"
  - "**/*.vue"
  - "**/*.svelte"
  - "**/styles/**"
  - "**/*.css"
  - "**/*.scss"
  - "**/*.less"
---

# Frontend Development Standards

## Core Principles
- Mobile-first responsive design
- Accessibility (WCAG 2.1 AA) as a requirement, not an afterthought
- Performance budgets for bundle size and load time
- Component-driven architecture

## Component Architecture

### DO: Create small, focused components
```tsx
// Good - Single responsibility
const UserAvatar: React.FC<UserAvatarProps> = ({ user, size = 'md' }) => (
  <img
    src={user.avatarUrl}
    alt={`${user.name}'s avatar`}
    className={cn('rounded-full', sizeClasses[size])}
  />
);

// Compose into larger components
const UserCard: React.FC<UserCardProps> = ({ user }) => (
  <div className="flex items-center gap-3">
    <UserAvatar user={user} />
    <UserName user={user} />
  </div>
);
```

### DON'T: Create monolithic components
```tsx
// Avoid - Too many responsibilities
const UserSection = ({ users, onEdit, onDelete, filter, sort, ...props }) => {
  // 500+ lines of mixed concerns
};
```

## State Management

### Use appropriate state location
| State Type | Location | Example |
|------------|----------|---------|
| Local UI | useState | Form input, dropdown open |
| Shared UI | Context | Theme, sidebar open |
| Server | React Query/SWR | User data, products |
| Global app | Zustand/Redux | Auth, cart |

## Accessibility

### Required for all interactive elements
```tsx
// Buttons
<button
  type="button"
  onClick={handleClick}
  aria-label="Close dialog"
  disabled={isLoading}
>
  <CloseIcon aria-hidden="true" />
</button>

// Forms
<label htmlFor="email">Email address</label>
<input
  id="email"
  type="email"
  aria-describedby="email-error"
  aria-invalid={hasError}
/>
{hasError && <p id="email-error" role="alert">{error}</p>}
```

### Use semantic HTML
```tsx
// Prefer
<nav aria-label="Main navigation">
<main>
<article>
<aside>
<header>
<footer>
<button>
<a href="/page">

// Avoid
<div onclick="...">
<span class="link">
```

## CSS & Styling

### Use design tokens
```css
:root {
  --color-primary-500: #3b82f6;
  --color-gray-100: #f3f4f6;
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-4: 1rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
}
```

### Mobile-first responsive design
```css
/* Base styles for mobile */
.card {
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
}

/* Tablet and up */
@media (min-width: 768px) {
  .card {
    flex-direction: row;
    padding: var(--space-6);
  }
}
```

## Performance

### Optimize bundle size
```tsx
// Lazy load routes and heavy components
const Dashboard = lazy(() => import('./pages/Dashboard'));

// Tree-shakeable imports
import { Button } from '@/components/ui/button';  // Good
import * as UI from '@/components/ui';  // Avoid - Imports everything
```

### Memoize expensive operations
```tsx
const sortedItems = useMemo(
  () => items.slice().sort((a, b) => b.date - a.date),
  [items]
);

const handleSubmit = useCallback(
  (data: FormData) => { mutation.mutate(data); },
  [mutation]
);
```

## Error Handling

### Implement error boundaries
```tsx
class ErrorBoundary extends Component<Props, State> {
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} onRetry={this.reset} />;
    }
    return this.props.children;
  }
}
```

### Handle loading and error states
```tsx
const UserProfile: React.FC<{ userId: string }> = ({ userId }) => {
  const { data: user, isLoading, error } = useQuery(['user', userId], fetchUser);

  if (isLoading) return <ProfileSkeleton />;
  if (error) return <ErrorMessage error={error} />;
  if (!user) return <NotFound />;

  return <Profile user={user} />;
};
```

## File Organization
```
src/
├── components/
│   ├── ui/                 # Primitive components (Button, Input)
│   ├── features/           # Feature-specific components
│   └── layouts/            # Layout components
├── hooks/                  # Custom hooks
├── lib/                    # Utilities and helpers
├── styles/                 # Global styles
└── pages/ or app/          # Route components
```
