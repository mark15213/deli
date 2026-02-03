# Backend API Reference

Base URL: `/api/v1`

## Authentication (`/auth`)

### Notion Login
- **GET** `/auth/notion/login`
- Redirects user to Notion OAuth authorization page.

### Notion Callback
- **GET** `/auth/notion/callback`
- **Query Params**: `code` (string)
- **Query Params**: `code` (string)
- **Response**: `Token` object (access_token, refresh_token, token_type, user_id, email).

### Refresh Token
- **POST** `/auth/refresh`
- **Body**:
  ```json
  { "refresh_token": "..." }
  ```
- **Response**: `Token` object with new access token.

## Sources (`/sources`) [NEW]
Manage external data sources (X, Notion, GitHub, etc).

### List Sources
- **GET** `/sources/`
- **Response**: List of Source objects.

### Create Source
- **POST** `/sources/`
- **Body**:
  ```json
  {
    "name": "My Source",
    "type": "X_SOCIAL",
    "connection_config": { ... },
    "ingestion_rules": { ... }
  }
  ```

### Get Source
- **GET** `/sources/{source_id}`

### Update Source
- **PUT** `/sources/{source_id}`
- **Body**: `SourceCreate` object (name, config, rules).

### Delete Source
- **DELETE** `/sources/{source_id}`

### Trigger Sync
- **POST** `/sources/{source_id}/sync`
- Manually triggers a sync job for this source.

## Quizzes (`/quizzes`)

### Get Today's Queue
- **GET** `/quizzes/today`
- **Response**: List of cards due for review.

### Get Quiz Card
- **GET** `/quizzes/{card_id}`

### Get Quiz Answer
- **GET** `/quizzes/{card_id}/answer`

### Submit Review
- **POST** `/quizzes/{card_id}/review`
- **Body**:
  ```json
  { "rating": 3 } // 1=Again, 2=Hard, 3=Good, 4=Easy
  ```

## Inbox (`/inbox`)

### Get Pending Items
- **GET** `/inbox/pending`
- **Response**: List of cards waiting for approval.

### Approve Item
- **POST** `/inbox/{card_id}/approve`

### Reject Item
- **POST** `/inbox/{card_id}/reject`

## Statistics (`/stats`)

### Get Dashboard Stats
- **GET** `/stats/dashboard`

## Sync (Legacy) (`/sync`)

### Trigger Sync
- **POST** `/sync/trigger`
- Triggers sync for legacy SyncConfigs.

### Sync Status
- **GET** `/sync/status`
