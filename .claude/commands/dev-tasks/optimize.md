---
name: optimize
description: Optimize code for better performance
---

# /optimize - Optimize Performance

Analyze and optimize code for better performance.

## Optimization Areas

1. **Time Complexity** - Reduce algorithmic complexity
2. **Space Complexity** - Minimize memory usage
3. **I/O Operations** - Batch, cache, or parallelize
4. **Rendering** - Reduce re-renders, virtualize lists (frontend)
5. **Database** - Query optimization, indexing (backend)

## Process

1. Read and analyze the target code
2. Identify performance bottlenecks
3. Measure or estimate current performance characteristics
4. Apply optimizations while maintaining correctness
5. Document trade-offs

## Optimization Checklist

### General
- [ ] Remove unnecessary operations inside loops
- [ ] Use appropriate data structures (Set vs Array, Map vs Object)
- [ ] Avoid redundant calculations (memoization)
- [ ] Batch I/O operations where possible

### Frontend
- [ ] Reduce re-renders (useMemo, useCallback, React.memo)
- [ ] Virtualize long lists
- [ ] Lazy load components and routes
- [ ] Optimize images and assets

### Backend
- [ ] N+1 query prevention
- [ ] Proper database indexing
- [ ] Connection pooling
- [ ] Caching strategies
- [ ] Async/parallel processing

## Output Format

```markdown
## Performance Analysis

### Current Issues
- [Issue 1]: [Impact]
- [Issue 2]: [Impact]

### Optimizations Applied

#### [Optimization 1]
**Before**: [Description or code]
**After**: [Description or code]
**Improvement**: [Expected improvement]

### Optimized Code
[The optimized code]

### Trade-offs
- [Trade-off 1]: [e.g., Memory vs Speed]

### Benchmarks (if applicable)
| Metric | Before | After |
|--------|--------|-------|
| [Metric] | [Value] | [Value] |
```

## Arguments

$ARGUMENTS

If a file path is provided, optimize that file.
If specific functions are mentioned, focus on those.
