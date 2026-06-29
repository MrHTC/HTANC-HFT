---
intent: 001-ai-trading-signals
phase: inception
status: context-defined
updated: 2026-06-18T01:25:00Z
---

# AI Trading Signals - System Context

## System Overview
An AI-powered trading signal generation system that ingests market data from multiple sources, applies deep learning models (LSTM/transformers), and delivers actionable buy/sell/hold signals to traders via dashboard and notifications.

## Context Diagram

```mermaid
C4Context
    title System Context - AI Trading Signals

    Person(trader, "Trader", "Views signals, configures preferences, reviews performance")
    Person(admin, "Admin", "Manages models, data sources, system configuration")

    System(sys, "AI Trading Signals", "Generates trading signals using deep learning models")

    System_Ext(marketData, "Market Data Providers", "External APIs for price/volume data (stocks, crypto, forex)")
    System_Ext(notification, "Notification System", "Push alerts and notifications for high-confidence signals")
    System_Ext(backtest, "Backtesting Engine", "Historical performance testing and model evaluation")

    Rel(trader, sys, "Views signals and configures preferences")
    Rel(admin, sys, "Manages models and data sources")
    Rel(sys, marketData, "Fetches real-time and historical data")
    Rel(sys, notification, "Sends high-confidence signal alerts")
    Rel(sys, backtest, "Runs historical performance tests")
```

## External Integrations

- **Market Data Providers**: Multiple aggregated sources for stocks, crypto, and forex price/volume data
- **Notification System**: Push alerts for high-confidence signals via dashboard and configured channels
- **Backtesting Engine**: Automated historical performance testing and model evaluation against historical data

## High-Level Constraints

- Must use existing Supabase PostgreSQL for signal and performance data storage
- ML models deployable via FastAPI
- Frontend dashboard built with Next.js

## Key NFR Goals

- Signal generation latency < 1 second
- Support 1,000+ concurrent dashboard users
- 99.5% uptime for signal generation service
- Deep learning model inference optimized for real-time performance
