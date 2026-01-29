# Mermaid Diagram Patterns

Reference patterns for common diagram types. Load this when creating diagrams.

## Flow: How Data Moves

Use `sequenceDiagram` for interactions between actors:

```mermaid
sequenceDiagram
    participant U as User
    participant C as Client
    participant S as Server
    participant D as Database

    U->>C: Types message
    C->>S: POST /messages
    S->>D: INSERT message
    D-->>S: message_id
    S-->>C: 201 Created
    C-->>U: Shows confirmation
```

## Structure: How Things Relate

Use `classDiagram` for inheritance and composition:

```mermaid
classDiagram
    class BaseView {
        +render()
        +update()
    }
    class ListView {
        +items[]
        +renderList()
    }
    class DetailView {
        +item
        +renderDetail()
    }

    BaseView <|-- ListView
    BaseView <|-- DetailView
```

## Architecture: How Systems Connect

Use `graph` for component relationships:

```mermaid
graph TB
    subgraph Frontend
        UI[User Interface]
        State[State Manager]
    end

    subgraph Backend
        API[API Server]
        Queue[Message Queue]
        Worker[Background Worker]
    end

    subgraph Data
        DB[(Database)]
        Cache[(Cache)]
    end

    UI --> State
    State --> API
    API --> DB
    API --> Cache
    API --> Queue
    Queue --> Worker
    Worker --> DB
```

## Lifecycle: How States Change

Use `stateDiagram-v2` for state machines:

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Submitted: submit()
    Submitted --> InReview: assign_reviewer()
    InReview --> Approved: approve()
    InReview --> Rejected: reject()
    Rejected --> Draft: revise()
    Approved --> Published: publish()
    Published --> [*]
```

## Tips

### Keep It Focused

One diagram, one idea. If you're trying to show everything, you're showing nothing.

Bad: "The entire system architecture with all data flows and state transitions"
Good: "How a user message reaches the AI and gets a response"

### Use Subgraphs for Grouping

When showing systems with boundaries:

```mermaid
graph LR
    subgraph Client
        A[Component A]
        B[Component B]
    end
    subgraph Server
        C[Service C]
        D[Service D]
    end
    A --> C
    B --> D
```

### Show Direction

Make data flow direction clear. Left-to-right or top-to-bottom for primary flow:

```mermaid
graph LR
    Input --> Process --> Output
```

### Label Edges

Don't just show connections - show what flows through them:

```mermaid
graph LR
    A -->|request| B
    B -->|response| A
```

### Include the User

System diagrams often forget the human. Include them:

```mermaid
graph LR
    User((User)) --> UI[Interface]
    UI --> System[System]
    System --> UI
    UI --> User
```
