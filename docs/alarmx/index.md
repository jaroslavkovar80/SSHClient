# mapp AlarmX

## Introduction
mapp AlarmX is a framework module providing centralized alarm handling,
visualization, and lifecycle management for mapp-based applications.

## Key Features
- Central alarm management
- Severity and priority handling
- Integration with mappView
- Configurable acknowledgment logic

## Typical Use Cases
- Machine alarm visualization
- Operator guidance
- Service diagnostics

## Architecture Overview
```mermaid
graph TD
  App --> AlarmX
  AlarmX --> AlarmCore
  AlarmX --> mappView