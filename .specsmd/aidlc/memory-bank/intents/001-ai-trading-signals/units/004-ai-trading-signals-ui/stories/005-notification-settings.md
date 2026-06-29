---
id: 005-notification-settings
unit: 004-ai-trading-signals-ui
intent: 001-ai-trading-signals
status: draft
priority: could
created: 2026-06-18T01:37:00Z
assigned_bolt: null
implemented: false
---

# Story: 005-notification-settings

## User Story

**As a** trader
**I want** to configure notification thresholds for high-confidence signals
**So that** I am alerted when important signals are generated

## Acceptance Criteria

- [ ] **Given** notification settings, **When** I set a confidence threshold, **Then** signals above that threshold trigger a notification
- [ ] **Given** notification is triggered, **When** a signal meets the threshold, **Then** I receive an in-app notification (toast/badge)
- [ ] **Given** notification preferences, **When** I configure per-instrument thresholds, **Then** only signals for configured instruments trigger notifications
- [ ] **Given** notification history, **When** I open the notification panel, **Then** I see recent notifications with signal details
- [ ] **Given** do-not-disturb mode, **When** enabled, **Then** notifications are suppressed until disabled

## Technical Notes

- In-app toast notifications via React context
- Notification preferences stored in local storage or user profile
- Badge counter on notification bell icon
- Future: push notifications via service worker

## Dependencies

### Requires
- 001-real-time-signal-feed

### Enables
- Proactive signal awareness

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| 50 signals above threshold in 1 minute | Batch into single "N signals generated" notification |
| User clears notifications | Reset badge counter |
| Threshold set to 100% | No notifications (impossible threshold) - show warning |
