# Web Search Feature Implementation

## Overview
Add the ability to search the web when local course materials don't have the answer. The AI can decide when to use web search (similar to how it decides to use CourseSearchTool).

## Implementation Steps

### Step 1: Add exa-py dependency
- File: `pyproject.toml`
- Action: Add `exa-py` to dependencies

### Step 2: Add EXA_API_KEY to Config
- File: `backend/config.py`
- Action: Add `EXA_API_KEY` field to Config dataclass

### Step 3: Create WebSearchTool class
- File: `backend/search_tools.py`
- Action: Create new `WebSearchTool` class inheriting from `Tool` ABC
- Uses Exa API to search the web
- Returns formatted results with sources/URLs

### Step 4: Register WebSearchTool
- File: `backend/rag_system.py`
- Action: Instantiate and register `WebSearchTool` with `ToolManager`

### Step 5: Update system prompt
- File: `backend/ai_generator.py`
- Action: Update system prompt to guide AI on when to use web vs local search

## Status
- [x] Step 1: Add exa-py dependency
- [x] Step 2: Add EXA_API_KEY to Config
- [x] Step 3: Create WebSearchTool class
- [x] Step 4: Register WebSearchTool
- [x] Step 5: Update system prompt

## Summary
Added web search capability using Exa API. The AI can now decide to use `search_web` when local course materials don't have the answer.

### Files Modified
1. `pyproject.toml` - Added `exa-py>=1.0.0` dependency
2. `backend/config.py` - Added `EXA_API_KEY` field
3. `backend/search_tools.py` - Added `WebSearchTool` class
4. `backend/rag_system.py` - Registered WebSearchTool with ToolManager
5. `backend/ai_generator.py` - Updated system prompt to guide AI on when to use web search

### Usage
Set `EXA_API_KEY` in your `.env` file to enable web search. The AI will automatically decide when to use it based on the system prompt instructions.