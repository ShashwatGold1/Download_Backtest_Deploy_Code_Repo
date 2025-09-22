Project Structure

Code folder: D:\Programming\Download_Backtest_Deploy - Contains all source code and scripts
Data folder: D:\Programming\Download_Backtest_Deploy_data - Contains all project data files and datasets in the same structure of the code folder

Note: Code and data are kept in separate folders for better organization and version control.

Project Context - Trading System

Project Type: Download_Backtest_Deploy - High-frequency algorithmic trading system
Trading Platform: DhanHQ API integration
Focus Areas: Data download, backtesting algorithms, deployment automation

Development Instructions

Trading Project Standards
- Role: High frequency algorithmic trader and developer
- Priority: Execution speed and minimal latency for high-frequency trading
- Code Quality: Clean, fast, efficient code optimization
- API Integration: Reliable DhanHQ API integration
- Performance: Algorithm efficiency for real-time trading operations

Feature Development Rules
- Prioritize execution speed and efficiency
- Maintain clean, readable code structure
- Optimize for minimal latency and maximum performance
- Focus on reliable API integration

File Management
- Only create files when absolutely necessary
- Always prefer editing existing files over creating new ones
- Never proactively create documentation files unless explicitly requested
- Always create proper .gitignore files

Automated Git Workflow
- Complete automation - user performs no manual git operations
- Mandatory staging, committing, and pushing for ALL code changes
- Commit format: [Commit number]: [message in 10 words max]
- Auto-triggers: New features, bug fixes, major updates, "Update project" command
- Always verify push success with git status

Bug Fixing Rule
- Always maintain original UI and project functionality when solving bugs

Large File Analysis Protocol

For any file exceeding context limits (>256k tokens):

1. **NEVER use Read tool** for large files (CSV, JSON, logs, datasets)
2. **ALWAYS use Grep tool** with progressive refinement approach:
   - Start broad: find relevant files using pattern matching
   - Narrow down: search specific patterns in target files
   - Extract precise: get exact matches with line numbers using -n=true
3. **Use strategic search patterns:**
   - output_mode="files_with_matches" for file discovery
   - output_mode="content" with -n=true for line numbers and content
   - Apply head_limit if results are too numerous
   - Use regex patterns for precision matching
4. **Token efficiency workflow:**
   - Search → Refine → Extract → Locate
   - Each step uses minimal tokens while maximizing information
   - Typical usage: 1k tokens vs millions (99%+ reduction)

Example Workflow:
```
Step 1: Grep(pattern="KEYWORD", glob="*.csv", output_mode="files_with_matches")
Step 2: Grep(pattern="SPECIFIC_PATTERN", path="target_file", output_mode="content", -n=true)  
Step 3: Grep(pattern="^EXACT_MATCH", path="target_file", output_mode="content", -n=true)
```

This protocol applies to: CSV files, log files, JSON datasets, database exports, any large structured data files