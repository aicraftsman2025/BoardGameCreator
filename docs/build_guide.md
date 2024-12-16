# Board Game Creator - Complete Documentation

## Table of Contents
1. [User Guide](#user-guide)
2. [Build Instructions](#build-instructions)
3. [Development Guide](#development-guide)

# User Guide

## Getting Started
[Previous user guide content...]

[All content from the previous user_guide.md]

---

# Build Instructions

## Prerequisites
[Previous build guide content...]

[All content from the previous build_guide.md]

---

# Development Guide

## Project Structure

Build the app for MaCOS
rm -rf build dist

# Build with clean environment
pyinstaller --clean BoardGameCreator.spec

# Optional: Sign the app (recommended)
codesign --force --deep --sign - dist/BoardGameCreator.app