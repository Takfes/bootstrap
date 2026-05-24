# Notion Query Patterns — Agent Operations Board

**Default database ID:** `35c0c6d6-81e1-80d9-b994-f1d67618be18`

Replace `$NOTION_API_TOKEN` from environment. The database ID is hardcoded below; override with `35c0c6d6-81e1-80d9-b994-f1d67618be18` if targeting a different board.

## All open tasks, ranked by priority

```bash
curl -s -X POST "https://api.notion.com/v1/databases/35c0c6d6-81e1-80d9-b994-f1d67618be18/query" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {"property": "Status", "select": {"does_not_equal": "Done"}},
    "sorts":  [{"property": "Priority", "direction": "ascending"}]
  }' | jq '.results[] | {
    id:          .id,
    title:       .properties.Name.title[0].text.content,
    status:      .properties.Status.select.name,
    priority:    .properties.Priority.select.name,
    effort:      .properties.Effort.select.name,
    type:        [.properties["Task Type"].multi_select[].name],
    description: (.properties.Description.rich_text[0].text.content // ""),
    assign:      (.properties.Assign.rich_text[0].text.content // ""),
    deadline:    (.properties.Deadline.date.start // "")
  }'
```

## Dispatch candidates (Backlog, non-Epic)

```bash
curl -s -X POST "https://api.notion.com/v1/databases/35c0c6d6-81e1-80d9-b994-f1d67618be18/query" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {
      "and": [
        {"property": "Status", "select": {"equals": "Backlog"}},
        {"property": "Effort", "select": {"does_not_equal": "Epic"}}
      ]
    },
    "sorts": [{"property": "Priority", "direction": "ascending"}]
  }' | jq '.results[] | {
    id:          .id,
    title:       .properties.Name.title[0].text.content,
    priority:    .properties.Priority.select.name,
    effort:      .properties.Effort.select.name,
    type:        [.properties["Task Type"].multi_select[].name],
    description: (.properties.Description.rich_text[0].text.content // "")
  }'
```

## Tasks by type

```bash
# Replace "skill-creation" with: coding / tooling-config / research
curl -s -X POST "https://api.notion.com/v1/databases/35c0c6d6-81e1-80d9-b994-f1d67618be18/query" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"filter": {"property": "Task Type", "multi_select": {"contains": "skill-creation"}}}' \
  | jq '.results[] | {id: .id, title: .properties.Name.title[0].text.content, status: .properties.Status.select.name}'
```

## Currently in progress

```bash
curl -s -X POST "https://api.notion.com/v1/databases/35c0c6d6-81e1-80d9-b994-f1d67618be18/query" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"filter": {"property": "Status", "select": {"equals": "In Progress"}}}' \
  | jq '.results[] | {id: .id, title: .properties.Name.title[0].text.content, assign: (.properties.Assign.rich_text[0].text.content // "unassigned")}'
```

## Awaiting review

```bash
-d '{"filter": {"property": "Status", "select": {"equals": "Review"}}}'
```

## Epics (need decomposition)

```bash
-d '{"filter": {"property": "Effort", "select": {"equals": "Epic"}}}'
```

## Create a task

```bash
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent":     {"database_id": "'"35c0c6d6-81e1-80d9-b994-f1d67618be18"'"},
    "properties": {
      "Name":        {"title":       [{"text": {"content": "Task title"}}]},
      "Status":      {"select":      {"name": "Backlog"}},
      "Priority":    {"select":      {"name": "P2 – Medium"}},
      "Effort":      {"select":      {"name": "M"}},
      "Task Type":   {"multi_select": [{"name": "coding"}]},
      "Description": {"rich_text":   [{"text": {"content": "What the agent should do."}}]}
    }
  }' | jq '{id: .id, title: .properties.Name.title[0].text.content}'
```

## Update a single property

```bash
curl -s -X PATCH "https://api.notion.com/v1/pages/<page_id>" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"properties": {"Status": {"select": {"name": "In Progress"}}, "Assign": {"rich_text": [{"text": {"content": "python-pro"}}]}}}' \
  | jq '{id: .id, status: .properties.Status.select.name}'
```

## MCP equivalents

All queries above work with `mcp__notion__query_database` or `mcp__notion__update_page` — pass the same filter/sort JSON bodies directly.
