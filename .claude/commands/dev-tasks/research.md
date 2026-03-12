---
name: research
description: Search Archon knowledge base for documentation and code examples
---

# /research - Research Topic

Search the Archon knowledge base for documentation and code examples.

## Search Workflow

### 1. Get Available Sources

```python
rag_get_available_sources()
```

This returns a list of documentation sources with their IDs.

### 2. Search Documentation

```python
# General search (2-5 keywords work best)
rag_search_knowledge_base(query="authentication JWT", match_count=5)

# Search specific source
rag_search_knowledge_base(query="vector functions", source_id="src_abc123")
```

### 3. Find Code Examples

```python
rag_search_code_examples(query="React hooks", match_count=3)
```

### 4. Read Full Page

```python
rag_read_full_page(page_id="...")
rag_read_full_page(url="...")
```

## Query Best Practices

| Good Queries | Bad Queries |
|--------------|-------------|
| `authentication JWT` | `how to implement user authentication` |
| `React useState` | `React hooks useState useEffect` |
| `pgvector similarity` | `implement vector search in PostgreSQL` |
| `FastAPI middleware` | `how to create middleware in FastAPI` |

**Keep queries to 2-5 keywords for best results.**

## Research Report Template

```markdown
## Research: [Topic]

### Query Used
`[search query]`

### Key Findings

#### Finding 1: [Title]
- **Source**: [URL/page]
- **Summary**: [Key points]
- **Relevance**: [How it applies]

#### Finding 2: [Title]
...

### Code Examples

[Relevant code examples found]

### Recommendations

1. [Recommendation based on findings]
2. [Alternative approach if applicable]

### Related Topics to Explore

- [Topic 1]
- [Topic 2]
```

## Web Search (Alternative)

If RAG sources are insufficient, use web search:

```python
mcp__brave-search__brave_web_search(query="topic keyword")
```

## Arguments

$ARGUMENTS

If a topic is provided, search for it directly.
If no topic, ask what to research.
