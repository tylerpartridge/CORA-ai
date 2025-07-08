# 🚨 Cursor Behavior Control

## The Problem
Cursor tends to be overly helpful - creating entire solutions when asked simple questions.

## The Solution
Explicit behavioral rules in BOOTUP.md:
1. NEVER create/modify files unless explicitly asked
2. DEFAULT BEHAVIOR: Answer questions, don't implement

## Test Phrases That Should NOT Trigger File Creation
- "Where should I put X?"
- "What folder does Y go in?"
- "How would I organize Z?"
- "What's the best location for...?"

## Phrases That SHOULD Trigger File Creation
- "Create a file for..."
- "Please implement..."
- "Add a new..."
- "Modify the existing..."

## Failed Test #2 Analysis
**Input:** "Where should I put API config?"
**Expected:** "data/ folder"
**Actual:** Created 4 files, modified app.py
**Root Cause:** No explicit "don't create" rule

## Enforcement
The updated BOOTUP.md now has:
- Rule #1: NEVER create/modify without permission
- Rule #2: Answer location questions with locations only
- DEFAULT BEHAVIOR explicitly stated