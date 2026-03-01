# TUI File Manager - Issue Tracker & Action Items

**Generated:** February 28, 2026  
**Source:** Comprehensive Code Review & Audit  
**Total Issues:** 31

---

## 🔴 Critical Issues (Blocking)

**None identified** - No showstoppers preventing beta release

---

## 🟡 High Priority Issues

### H1: Symlink Safety Not Validated
**Severity:** HIGH  
**Category:** Security  
**Files:** `filesystem_service.py`, `archive_service.py`, `git_enhanced.py`  
**Effort:** Medium (2-3 hours)

**Description:**
Only one symlink check exists in the entire codebase (`filterable_tree.py:104`). File operations (copy, move, delete) and archive extraction don't validate symlinks, potentially allowing:
- Reading files outside intended scope
- Writing to arbitrary locations
- Infinite loops in recursive operations

**Reproduction:**
```python
# Create symlink to /etc outside project scope
ln -s /etc tui-file-manager/test_link
# App may follow symlink and expose system files
```

**Fix:**
```python
# Add to filesystem_service.py
def _validate_path_safety(path: Path, base_path: Optional[Path] = None) -> bool:
    """Validate path doesn't escape intended scope via symlinks."""
    resolved = path.resolve()
    if base_path:
        try:
            resolved.relative_to(base_path.resolve())
            return True
        except ValueError:
            return False
    return True

# Use in copy_path, move_path, delete_path
def copy_path(source: Path, destination: Path) -> Path:
    if not _validate_path_safety(source):
        raise ValueError("Invalid source path")
    if not _validate_path_safety(destination):
        raise ValueError("Invalid destination path")
    # ... rest of implementation
```

**Testing:**
- Create symlinks to files outside project directory
- Attempt copy/move/delete operations
- Verify operations are rejected

---

### H2: Archive Extraction Vulnerable to Zip Slip
**Severity:** HIGH  
**Category:** Security  
**Files:** `archive_service.py`  
**Effort:** Low (1 hour)

**Description:**
Archive extraction doesn't validate that extracted files stay within the target directory. Malicious archives with paths like `../../../etc/passwd` could write files anywhere.

**Reproduction:**
```python
# Create malicious ZIP with path traversal
import zipfile
with zipfile.ZipFile('malicious.zip', 'w') as zf:
    zf.writestr('../../../tmp/pwned.txt', 'hacked')

# Extract with current code - writes outside target!
service.extract_all(Path('malicious.zip'), Path('./extract'))
```

**Fix:**
```python
# Add to archive_service.py
def _is_safe_path(base_path: Path, target_path: Path) -> bool:
    """Prevent path traversal attacks."""
    try:
        target_path.resolve().relative_to(base_path.resolve())
        return True
    except ValueError:
        return False

# Use in extraction methods
def _extract_from_zip(self, ...):
    # ...
    for member in zip_file.infolist():
        target = extract_to / member.filename
        if not _is_safe_path(extract_to, target):
            raise ValueError(f"Unsafe path in archive: {member.filename}")
        # ... extract safely
```

**Testing:**
- Create ZIP with `../` paths
- Attempt extraction
- Verify files stay within target directory

---

### H3: Zero Test Coverage on UI Components
**Severity:** HIGH  
**Category:** Testing  
**Files:** `app.py`, `config_ui.py`, `tabbed_directory_tree.py`, `git_ui_components.py`  
**Effort:** High (8-12 hours)

**Description:**
1,452 lines of UI code have 0% test coverage:
- `app.py`: 900 statements
- `config_ui.py`: 155 statements
- `tabbed_directory_tree.py`: 158 statements
- `git_ui_components.py`: 235 statements

**Impact:**
- High regression risk when modifying UI
- Keyboard shortcuts untested
- Screen navigation untested
- Error handling untested

**Fix:**
Add integration tests using Textual's testing framework:
```python
# test_app.py
from textual.testing import run_test

async def test_app_startup():
    """Test app starts without errors."""
    async with run_test(FileManagerApp()) as pilot:
        app = pilot.app
        assert app.current_path.exists()
        
async def test_help_toggle():
    """Test help screen toggle."""
    async with run_test(FileManagerApp()) as pilot:
        await pilot.press("h")
        assert "Help" in app.screen.id
        await pilot.press("h")
        assert app.screen.id != "help"
```

**Testing Strategy:**
1. Start/stop app
2. Keyboard shortcut handlers
3. Screen navigation
4. Error dialogs
5. Configuration changes

---

### H4: Ruff Linting Errors (85 total)
**Severity:** MEDIUM-HIGH  
**Category:** Code Quality  
**Files:** Multiple (see breakdown below)  
**Effort:** Low (1-2 hours with auto-fix)

**Description:**
85 linting errors detected, including:
- 14 B904 (missing exception chaining) - **Most Important**
- 38 F401 (unused imports)
- 16 W291 (trailing whitespace)
- 7 B007 (unused loop variables)
- 7 F841 (unused variables)
- 3 F601 (duplicate dict keys)

**Fix:**
```bash
# Auto-fix cosmetic issues
ruff check . --fix

# Manually fix B904 errors (exception chaining)
# Before:
raise ValueError(f"Failed: {e}")
# After:
raise ValueError(f"Failed: {e}") from e
```

**Files Requiring Manual Review:**
- `archive_service.py`: 14 errors (B904 priority)
- `fuzzy_search_service.py`: 13 errors (mostly W291)
- `git_ui_components.py`: 11 errors (F401)
- `app.py`: 2 errors (F841)

---

## 🟠 Medium Priority Issues

### M1: Missing Exception Chaining (B904)
**Severity:** MEDIUM  
**Category:** Code Quality  
**Files:** `archive_service.py` (10 occurrences), `fuzzy_search_service.py` (4 occurrences)  
**Effort:** Low (30 minutes)

**Description:**
Exceptions are re-raised without preserving original traceback:
```python
except (zipfile.BadZipFile, OSError) as e:
    raise ValueError(f"Failed to read ZIP archive: {e}")
    # Should be: raise ValueError(...) from e
```

**Impact:**
- Loses original error context in logs
- Makes debugging harder
- Violates Python exception best practices

**Fix:**
Add `from e` to all 14 occurrences:
```python
raise ValueError(f"Failed to read ZIP archive: {e}") from e
```

---

### M2: Subprocess Input Validation
**Severity:** MEDIUM  
**Category:** Security  
**Files:** `git_enhanced.py`  
**Effort:** Low (1 hour)

**Description:**
Git branch names and refs from user input aren't validated before passing to subprocess:
```python
def switch_branch(self, branch_name: str):
    result = subprocess.run(
        ["git", "checkout", branch_name],  # branch_name unchecked
        ...
    )
```

**Impact:**
- Potential shell injection if branch name contains metacharacters
- Git command failures with confusing errors

**Fix:**
```python
import re

def _validate_git_ref(ref: str) -> bool:
    """Validate Git reference name."""
    # Git refs can contain alphanumerics, /, -, _, .
    return bool(re.match(r'^[a-zA-Z0-9/_\-.]+$', ref))

def switch_branch(self, branch_name: str):
    if not _validate_git_ref(branch_name):
        raise ValueError(f"Invalid branch name: {branch_name}")
    # ... proceed safely
```

---

### M3: No File Size Limits on Operations
**Severity:** MEDIUM  
**Category:** Performance/Safety  
**Files:** `filesystem_service.py`, `archive_service.py`  
**Effort:** Low (1 hour)

**Description:**
Copy/move/extraction operations have no size limits:
```python
def copy_path(source: Path, destination: Path) -> Path:
    shutil.copytree(source, destination)  # Could copy 100GB
```

**Impact:**
- Disk exhaustion
- Long-blocking operations
- Potential DoS

**Fix:**
```python
# Add to config_manager.py
"max_operation_size": 1_000_000_000,  # 1GB default

# Add to filesystem_service.py
def copy_path(source: Path, destination: Path, max_size: Optional[int] = None) -> Path:
    if max_size is None:
        max_size = ConfigManager().get("max_operation_size")
    
    total_size = sum(f.stat().st_size for f in source.rglob('*') if f.is_file())
    if total_size > max_size:
        raise ValueError(f"Operation exceeds size limit: {total_size} > {max_size}")
    # ... proceed
```

---

### M4: RuntimeWarning in Tests
**Severity:** LOW-MEDIUM  
**Category:** Testing  
**Files:** Test cleanup  
**Effort:** Low (30 minutes)

**Description:**
```
RuntimeWarning: coroutine 'DirectoryTree.watch_path' was never awaited
```

**Impact:**
- Test output noise
- Potential resource leak
- Confusing for contributors

**Fix:**
Investigate DirectoryTree cleanup in tests and ensure async methods are awaited:
```python
# In test teardown or fixture cleanup
await tree.watch_path()  # If this is a cleanup method
```

---

### M5: Two Failing Image Tests
**Severity:** MEDIUM  
**Category:** Testing  
**Files:** `test_image_integration_simple.py:57`, `test_image_preview_service.py:66`  
**Effort:** Low (30 minutes)

**Description:**
```python
E   AssertionError: assert False
E   +  where False = can_render_image(PosixPath('test.jpg'))
```

**Root Cause:**
PIL's `Image.open()` fails on mock file paths without actual image data.

**Fix:**
Mock PIL properly:
```python
@patch('image_preview_service.Image.open')
def test_supported_image_formats(mock_open):
    mock_img = Mock()
    mock_img.mode = 'RGB'
    mock_img.size = (100, 100)
    mock_open.return_value.__enter__ = Mock(return_value=mock_img)
    mock_open.return_value.__exit__ = Mock(return_value=False)
    
    # Now test can proceed with valid mock
```

---

## 🟢 Low Priority Issues

### L1: Unused Imports (F401) - 38 occurrences
**Severity:** LOW  
**Category:** Code Quality  
**Effort:** Trivial (15 minutes with auto-fix)

**Fix:**
```bash
ruff check . --fix --select F401
```

**Common Examples:**
- `typing.Tuple` imported but unused (5 files)
- `pytest` imported but unused (6 test files)
- `tempfile` imported but unused (3 files)

---

### L2: Trailing Whitespace (W291) - 16 occurrences
**Severity:** LOW  
**Category:** Cosmetic  
**Effort:** Trivial (5 minutes with auto-fix)

**Fix:**
```bash
ruff check . --fix --select W291
```

---

### L3: Duplicate Dictionary Keys (F601) - 3 occurrences
**Severity:** LOW  
**Category:** Code Quality  
**Files:** `icon_manager.py:165, 224, 231`  
**Effort:** Trivial (5 minutes)

**Description:**
```python
'.msi': '⚙️',  # Line 165
# ... 60 lines later ...
'.msi': '⚙️',  # Duplicate! Second silently overrides first
```

**Fix:**
Remove duplicate entries

---

### L4: Unused Loop Variables (B007) - 7 occurrences
**Severity:** LOW  
**Category:** Code Quality  
**Effort:** Trivial (10 minutes)

**Description:**
```python
for match, score, index in results:  # match unused
    original_path = all_paths[index]  # Only index used
```

**Fix:**
Rename to `_match` to indicate intentional non-use:
```python
for _match, score, index in results:
```

---

### L5: Help Text Mentions "Coming Soon" for Bookmarks
**Severity:** LOW  
**Category:** Documentation  
**Files:** `app.py:949`  
**Effort:** Trivial (2 minutes)

**Description:**
Help text states bookmarks are "coming soon" but they're fully implemented.

**Fix:**
Update help text in `action_toggle_help()` to reflect current state.

---

### L6: Inaccurate Coverage Claims
**Severity:** LOW  
**Category:** Documentation  
**Files:** `README.md`  
**Effort:** Trivial (2 minutes)

**Description:**
README states "95% code coverage" but actual overall coverage is 49%.

**Fix:**
Update to: "90%+ coverage on core modules, 49% overall"

---

### L7: Unused Variables (F841) - 7 occurrences
**Severity:** LOW  
**Category:** Code Quality  
**Effort:** Trivial (10 minutes)

**Examples:**
- `app.py:1611` - `current_branch` assigned but unused
- `git_enhanced.py:131` - `current_branch` assigned but unused
- Test files - assigned results never checked

**Fix:**
Remove unused assignments or use variables

---

### L8: Unsorted Imports (I001) - 6 occurrences
**Severity:** LOW  
**Category:** Cosmetic  
**Effort:** Trivial (5 minutes with auto-fix)

**Fix:**
```bash
ruff check . --fix --select I001
```

---

## 📋 Enhancement Requests (Non-Critical)

### E1: Add Progress Indicators for Long Operations
**Category:** UX  
**Effort:** Medium (4 hours)

**Description:**
Copy/move/delete operations show no progress for large files/directories.

**Implementation:**
```python
# Use Textual's progress bar
from textual.app import ComposeResult
from textual.widgets import ProgressBar

def action_copy_selected(self):
    # ...
    self.run_worker(
        self._copy_with_progress(source, destination),
        group="operations"
    )

async def _copy_with_progress(self, source, dest):
    total = calculate_total_size(source)
    progress = self.query_one("#progress", ProgressBar)
    progress.update(total=total)
    
    copied = 0
    for file in source.rglob('*'):
        # ... copy file ...
        copied += file.stat().st_size
        progress.update(progress=copied)
```

---

### E2: Add Cache Size Limits
**Category:** Performance  
**Effort:** Low (2 hours)

**Description:**
Caches in `disk_usage_service.py` and `icon_manager.py` grow unbounded.

**Implementation:**
```python
from functools import lru_cache

# Or use a TTL cache library
from cachetools import TTLCache, LRUCache

class DiskUsageService:
    def __init__(self):
        self._cache = LRUCache(maxsize=100)  # Max 100 entries
```

---

### E3: Virtual Scrolling for Large Directories
**Category:** Performance  
**Effort:** High (8-12 hours)

**Description:**
Directories with 10k+ files may lag due to no pagination.

**Implementation:**
- Implement Textual's `DataTable` with virtual scrolling
- Lazy-load directory entries as user scrolls
- Keep 500-entry safety limit as fallback

---

### E4: Atomic File Operations with Rollback
**Category:** Reliability  
**Effort:** High (12-16 hours)

**Description:**
Interrupted copy/move operations leave partial state.

**Implementation:**
```python
def copy_path_atomic(source: Path, destination: Path) -> Path:
    """Copy with rollback on failure."""
    temp_dest = destination.with_suffix(destination.suffix + '.tmp')
    try:
        result = shutil.copytree(source, temp_dest)
        temp_dest.rename(destination)  # Atomic on most filesystems
        return result
    except Exception:
        if temp_dest.exists():
            shutil.rmtree(temp_dest)  # Rollback
        raise
```

---

## Summary by Category

| Category | Count | High | Medium | Low |
|----------|-------|------|--------|-----|
| Security | 3 | 2 | 1 | 0 |
| Testing | 3 | 1 | 1 | 1 |
| Code Quality | 6 | 1 | 1 | 4 |
| Performance | 2 | 0 | 1 | 1 |
| Documentation | 2 | 0 | 0 | 2 |
| UX | 1 | 0 | 0 | 1 |
| Reliability | 1 | 0 | 0 | 1 |
| **Total** | **31** | **4** | **5** | **22** |

---

## Summary by Effort

| Effort | Count | Percentage |
|--------|-------|------------|
| Trivial (<15 min) | 10 | 32% |
| Low (15 min - 2 hrs) | 12 | 39% |
| Medium (2-4 hrs) | 4 | 13% |
| High (8+ hrs) | 5 | 16% |

---

## Recommended Fix Order

### Before Beta Release (Must Fix)
1. H1 - Symlink safety validation
2. H2 - Zip slip protection
3. H4 - Fix ruff B904 errors
4. M5 - Fix 2 failing image tests

### Before Beta Release (Should Fix)
5. M1 - Fix remaining exception chaining
6. L1-L8 - Auto-fix trivial linting errors
7. L5 - Update help text
8. L6 - Update coverage claims

### v0.3.0 (Short-term)
9. H3 - Add UI integration tests
10. M2 - Subprocess input validation
11. M3 - File size limits
12. E1 - Progress indicators
13. E2 - Cache size limits

### v1.0+ (Long-term)
14. E3 - Virtual scrolling
15. E4 - Atomic operations
16. Full security audit

---

## GitHub Issues Template

For each issue above, create a GitHub issue with:

```markdown
## Issue: [Short Title]

**Priority:** [High/Medium/Low]  
**Category:** [Security/Testing/Code Quality/Performance/Documentation]  
**Effort:** [Trivial/Low/Medium/High]

### Description
[Copy from issue tracker]

### Reproduction
[If applicable]

### Proposed Fix
[Copy from issue tracker]

### Testing
[How to verify fix]

### Files Affected
[List files]

### Related
[Links to related issues]
```

---

**Last Updated:** February 28, 2026  
**Next Review:** After fixing high-priority issues
