---
skill: excavate
description: Progressively discover and document features in an existing codebase
artifact_path: .lore/specs
---

# Excavate: Progressive Design Discovery

## Purpose

Document an existing codebase **one feature at a time**. Each excavation produces one spec file. Features link to other features, building a map incrementally.

This is the opposite of trying to understand everything at once.

## The Problem with "Survey Everything First"

Trying to document a 100k LOC codebase by surveying all of it first leads to:
- One massive, unusable document
- Analysis paralysis
- Features that blur together
- No clear stopping point

## The Progressive Discovery Approach

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Pick Entry Point  →  Trace Feature  →  Document Feature       │
│         ↑                                      │                │
│         │                                      ↓                │
│         └──────────  Discover Connections  ────┘                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

Each cycle produces **one spec file** for **one feature**.

Features can be:
- **Leaf features**: Do one thing (e.g., "password reset")
- **Container features**: Provide access to other features (e.g., "dashboard")

A container feature's spec lists what it contains. You excavate those separately.

## Invocation

```
/lore-development:excavate
```

### First Run: Find Entry Points

On first invocation (no existing specs), the skill:
1. Performs a quick scan for entry points
2. Presents them as starting options
3. User picks one to excavate first

```
Found entry points:

  API Routes:
    • GET /           → src/routes/index.ts (home/dashboard)
    • POST /auth/*    → src/routes/auth.ts (authentication)
    • GET /products/* → src/routes/products.ts (catalog)

  CLI Commands:
    • npm start       → src/index.ts (app bootstrap)
    • npm run migrate → src/db/migrate.ts (database setup)

  UI Pages:
    • /              → src/pages/Home.tsx
    • /login         → src/pages/Login.tsx

Which would you like to excavate first?
```

### Subsequent Runs: Continue or Branch

With existing specs, the skill:
1. Shows what's been documented
2. Shows discovered-but-not-documented features
3. User picks what to excavate next

```
Excavation Progress:

  Documented:
    ✓ home-dashboard.md (links to: auth, products, cart)
    ✓ authentication.md (links to: user-profile)

  Discovered (not yet documented):
    ○ products (from: home-dashboard)
    ○ cart (from: home-dashboard)
    ○ user-profile (from: authentication)

  Unexplored entry points:
    • CLI: migrate, seed
    • API: /admin/*

What would you like to excavate next?
```

## The Excavation Process (Per Feature)

When you pick a feature to excavate:

### Step 1: Trace the Feature

Starting from the entry point, trace:
- What files are involved?
- What data does it touch?
- What other features does it call/depend on?
- What can the user DO with this feature?

### Step 2: Ask Clarifying Questions

The skill may not understand the business context:

```
Tracing "products" feature...

I found these capabilities:
  • List products (paginated)
  • Search products
  • View product details
  • Filter by category

Questions:
  1. Is "add to cart" part of products or a separate cart feature?
  2. The "wishlist" button - is that a distinct feature?
  3. Are product reviews part of this or their own thing?
```

Your answers shape the feature boundary.

### Step 3: Document the Feature

Produces a spec file:

```markdown
# Feature: Product Catalog

## What It Does

Users can browse, search, and view products available for purchase.

## Capabilities

- **Browse products**: Paginated list of all products
- **Search**: Full-text search by name, description
- **Filter**: By category, price range, availability
- **View details**: Product page with images, description, specs

## Entry Points

| Entry | Type | Handler |
|-------|------|---------|
| GET /products | API | src/routes/products.ts:list |
| GET /products/:id | API | src/routes/products.ts:show |
| GET /products/search | API | src/routes/products.ts:search |
| /products | Page | src/pages/Products.tsx |
| /products/:id | Page | src/pages/ProductDetail.tsx |

## Implementation

### Files Involved

| File | Role |
|------|------|
| src/routes/products.ts | API routes |
| src/services/product-service.ts | Business logic |
| src/models/product.ts | Data model |
| src/pages/Products.tsx | List UI |
| src/pages/ProductDetail.tsx | Detail UI |
| src/components/ProductCard.tsx | Shared component |

### Data

- **products** table: id, name, description, price, category_id, ...
- **categories** table: id, name, parent_id

### Dependencies

- Uses: authentication (optional, for personalization)
- Uses: categories (for filtering)

## Connected Features

| Feature | Relationship |
|---------|-------------|
| [shopping-cart](./shopping-cart.md) | "Add to cart" button |
| [product-reviews](./product-reviews.md) | Review section on detail page |
| [categories](./categories.md) | Category filtering |
| [search](./search.md) | Search functionality (shared?) |

## Notes

- Search uses Elasticsearch (see src/services/search-service.ts)
- Images stored in S3, URLs in product.images JSON array
- Price display respects user locale (src/utils/currency.ts)
```

### Step 4: Record Discoveries

The skill notes features discovered but not yet documented:
- shopping-cart (mentioned in product detail)
- product-reviews (embedded in product page)
- categories (used for filtering)

These become candidates for the next excavation.

## Feature Hierarchy

Features naturally form a hierarchy:

```
.lore/specs/
├── home-dashboard.md        # Container: links to main features
├── authentication.md        # Leaf: login, logout, register
├── authentication/
│   └── password-reset.md    # Sub-feature of auth
├── products.md              # Container: browsing products
├── products/
│   ├── search.md            # Sub-feature
│   └── reviews.md           # Sub-feature
└── shopping-cart.md         # Leaf: cart management
```

A container feature lists what it contains. You can excavate sub-features as needed.

## Tracking Progress

The skill maintains a discovery index:

```
.lore/excavations/
└── index.md                 # What's documented, what's discovered
```

```markdown
# Excavation Index

## Documented Features

| Feature | Spec | Excavated | Connected To |
|---------|------|-----------|--------------|
| Home Dashboard | [home-dashboard.md](../specs/home-dashboard.md) | 2025-01-28 | auth, products, cart |
| Authentication | [authentication.md](../specs/authentication.md) | 2025-01-28 | user-profile |

## Discovered (Not Yet Documented)

| Feature | Discovered From | Entry Point |
|---------|-----------------|-------------|
| products | home-dashboard | GET /products |
| cart | home-dashboard | GET /cart |
| user-profile | authentication | GET /profile |

## Unexplored Entry Points

| Entry Point | Type | Notes |
|-------------|------|-------|
| /admin/* | API | Admin interface |
| npm run seed | CLI | Database seeding |
```

## Parameters

```
/lore-development:excavate                    # Interactive: show progress, pick next
/lore-development:excavate feature=products   # Excavate specific feature
/lore-development:excavate entry=/api/admin   # Start from specific entry point
/lore-development:excavate continue           # Continue with first undocumented
```

## What Makes a Feature Boundary?

A feature is:
- **User-centric**: Defined by what users can DO, not by code structure
- **Cohesive**: The parts belong together conceptually
- **Bounded**: Has clear entry points and dependencies

Signs you've found a feature boundary:
- It has its own entry points (routes, commands, pages)
- It has its own data (tables, entities)
- It could theoretically be removed without breaking unrelated things
- Users would describe it as "a thing the app does"

Signs you should split:
- "This feature does two very different things"
- Entry points serve different user goals
- Data is unrelated

Signs you should merge:
- "These are really the same capability"
- Always used together
- Share all the same data

## Dealing with Cross-Cutting Concerns

Some code isn't a feature - it's infrastructure:
- Logging
- Error handling
- Authentication middleware
- Database connections
- Caching

Document these separately as **infrastructure specs**:

```
.lore/specs/
├── _infrastructure/
│   ├── logging.md
│   ├── error-handling.md
│   ├── caching.md
│   └── database.md
└── [feature specs...]
```

These are referenced by features but excavated differently (no user-facing entry points).

## Why This Works Better

### vs. "Document Everything"

| Approach | Problem |
|----------|---------|
| Survey all → Document all | Context overload, massive docs, no stopping point |
| Progressive discovery | Bounded scope, modular output, natural stopping points |

### vs. "One Big Spec"

| Approach | Problem |
|----------|---------|
| Single spec file | Unwieldy, hard to maintain, hard to navigate |
| Spec per feature | Each file is focused, cross-linked, independently useful |

### vs. "Follow Directory Structure"

| Approach | Problem |
|----------|---------|
| Document by module/folder | Features span modules, misses the user perspective |
| Document by feature | Captures what users care about, regardless of code structure |

## The Compound Effect

A feature can be a gateway to other features:

```
Home Dashboard
    ├── links to → Authentication
    │                 └── contains → Password Reset
    ├── links to → Product Catalog
    │                 ├── contains → Search
    │                 └── contains → Reviews
    └── links to → Shopping Cart
                      └── links to → Checkout
```

Each excavation:
1. Documents one node
2. Discovers edges to other nodes
3. Makes the next excavation easier (you know what you're looking for)

Over time, you build a complete map without ever trying to hold it all at once.

## Example Session

```
User: /lore-development:excavate