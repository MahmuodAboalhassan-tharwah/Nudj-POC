# Code Review: Notifications Feature

## Overview
- **Feature**: Notifications (In-app & Email)
- **Reviewer**: AI Assistant
- **Date**: 2026-02-08

## Findings

### Backend
1.  **Models**: `Notification` model is well-defined. Used `str` for `type` instead of `enum` in DB column for better flexibility/migrations, though enum is defined in Python.
2.  **Service**: `NotificationService` handles CRUD correctly. 
    - `mark_as_read` and `mark_all_as_read` correctly enforce `user_id` filtering.
    - Uses `scalars().all()` and `scalar()` for queries, which is standard for SQLAlchemy 2.0.
3.  **API**: Router endpoints are clean. 
    - `get_notifications` includes pagination via `limit` and `offset`.
    - `unread_only` flag is useful for the header UI.

### Frontend
1.  **API Hooks**: `notifications.api.ts` implements polling (30s) which is appropriate for a basic notification system. Uses standard React Query patterns.
2.  **UI Components**: `NotificationCenter` is well-structured.
    - Handles loading and empty states.
    - Uses `formatDistanceToNow` for readable timestamps.
    - Correctly triggers mutations for marking as read.

### Integration
- Header integration in `MainLayout.tsx` is clean and follows the established layout pattern.

## Recommendation
- [x] Backend looks solid.
- [x] Frontend looks solid.
- [ ] Consider adding a websocket for real-time notifications in the future, but polling is sufficient for V1.
