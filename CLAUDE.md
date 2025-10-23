# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**IMPORTANT: Always respond in Chinese (Simplified Chinese) when working with this repository.**

## Project Overview

This is a Cloudflare Email Routing temporary email generator CLI tool. It automates the creation, management, and deletion of temporary email addresses using the Cloudflare Email Routing API. Emails sent to temporary addresses are automatically forwarded to a verified real email address.

**Core Technology**: Python 3.6+ with zero external dependencies (uses only stdlib: `urllib`, `json`, `argparse`)

**Email Format**: Generates 8-character random lowercase letter email addresses (e.g., `abcdefgh@domain.com`). Optional prefix support for custom formats (e.g., `test-abcdefgh@domain.com`).

**Cross-platform support**: Linux/macOS (via shell script), Windows (via batch script)

## Architecture

### Entry Points

1. **temp-email.sh** (Linux/macOS): Shell wrapper that loads `.env` and invokes the Python script
2. **temp-email.bat** (Windows CMD): Batch wrapper that loads `.env` and invokes the Python script
3. **temp-email.ps1** (Windows PowerShell - Recommended): PowerShell wrapper that properly loads `.env` for PowerShell environments
4. **temp_email.py**: Core Python implementation

All wrappers follow the same pattern:
- Check for `.env` file existence
- Load environment variables from `.env`
- Verify Python installation
- Execute `temp_email.py` with all arguments passed through

### Core Components

**CloudflareEmailManager** class (`temp_email.py`):
- `__init__()`: Loads and validates environment variables from `.env`
- `_make_request()`: HTTP client using `urllib.request` (no external deps like `requests`)
- `generate_random_email()`: Creates random email addresses with format: `{8lowercase}@{domain}` (pure random) or `{prefix}-{8lowercase}@{domain}` (with prefix)
- `create_routing_rule()`: Creates Email Routing rules via Cloudflare API
- `list_routing_rules(verbose=False)`: Fetches all routing rules with automatic pagination support (up to 5000 records)
- `delete_routing_rule()`: Deletes a specific rule by ID
- `find_rule_by_email()`: Searches for a rule matching a specific email address

**Command handlers**:
- `create_email()`: Creates temporary email with optional custom prefix/address
- `list_emails()`: Displays all routing rules in a formatted table (supports `-v` for verbose pagination info)
- `delete_email()`: Deletes a specific email (with confirmation prompt)
- `delete_batch_emails()`: Batch deletes emails matching wildcard pattern (username only, uses `fnmatch`)
- `cleanup_emails()`: Deletes all routing rules (with confirmation prompt)
- `save_to_history()`: Optionally saves created emails to `temp_emails.json` (silent failure)

### API Integration

Uses Cloudflare API v4 endpoints:
- `POST /zones/{zone_id}/email/routing/rules` - Create routing rule
- `GET /zones/{zone_id}/email/routing/rules` - List all rules
- `DELETE /zones/{zone_id}/email/routing/rules/{rule_id}` - Delete rule

Authentication: Bearer token via `Authorization` header

## Configuration

**Required environment variables** (in `.env`):
- `CLOUDFLARE_API_TOKEN`: API token with `Zone.Email Routing Rules.Edit` permission
- `CLOUDFLARE_ZONE_ID`: Zone ID from Cloudflare Dashboard
- `FORWARD_TO_EMAIL`: Verified destination email for forwarding
- `EMAIL_DOMAIN`: Domain managed in Cloudflare (must have Email Routing enabled)

**Optional**:
- `EMAIL_PREFIX`: Default prefix for random emails (default: None - no prefix)
- `CLOUDFLARE_ACCOUNT_ID`: Account ID (not currently used in API calls)

## Development Commands

### Running the tool

**Linux/macOS:**
```bash
# Make scripts executable (first time only)
chmod +x temp-email.sh temp_email.py

# Create temporary email
./temp-email.sh create
./temp-email.sh create --prefix test
./temp-email.sh create --email custom-name@example.com

# List all emails
./temp-email.sh list

# Delete email
./temp-email.sh delete email@example.com
./temp-email.sh delete email@example.com -y  # skip confirmation

# Cleanup all
./temp-email.sh cleanup
./temp-email.sh cleanup -y  # skip confirmation
```

**Windows (PowerShell - Recommended):**
```powershell
.\temp-email.ps1 create
.\temp-email.ps1 create --no-prefix
.\temp-email.ps1 create --prefix test
.\temp-email.ps1 list
.\temp-email.ps1 delete email@example.com
.\temp-email.ps1 cleanup
```

**Windows (CMD):**
```cmd
temp-email.bat create
temp-email.bat list
temp-email.bat delete email@example.com
temp-email.bat cleanup
```

**Direct Python:**
```bash
# Load .env manually or set environment variables, then:
python3 temp_email.py create
python3 temp_email.py list
python3 temp_email.py delete <email>
python3 temp_email.py cleanup
```

### Testing

Run the example script to test basic functionality:
```bash
./test_example.sh
```

This creates a test email with prefix "example" and lists all emails.

## Important Implementation Details

### No External Dependencies
The tool deliberately uses only Python stdlib to avoid dependency management. This means:
- HTTP requests use `urllib.request` instead of `requests`
- No `python-dotenv` - `.env` is parsed by shell scripts
- All JSON handling uses stdlib `json` module

### Error Handling
- Missing environment variables cause immediate failure with clear error message
- HTTP errors (401, 403, etc.) are caught and displayed with response body
- API errors from Cloudflare are extracted from `errors` field in response
- Confirmation prompts (`-y` flag) prevent accidental deletion

### Email Address Generation
**Current Format (Updated):**
- **No prefix (default)**: `{random8}@{domain}` - e.g., `abcdefgh@domain.com`
- **With prefix**: `{prefix}-{random8}@{domain}` - e.g., `test-abcdefgh@domain.com`
- Random: 8 lowercase letters from `[a-z]` (no digits, no date)
- Users can override with `--email` to specify custom addresses
- Use `--no-prefix` flag or omit `--prefix` for pure random emails
- Use `--prefix TEXT` for custom prefix emails

### Pagination Support
**Automatic pagination for `list_routing_rules()`:**
- Fetches all routing rules across multiple pages (up to 5000 records)
- Each page retrieves 50 records (Cloudflare API max)
- Multiple detection mechanisms:
  - Checks if returned records < per_page count
  - Checks `result_info.total_count` and `result_info.total_pages`
  - Safety limit: max 100 pages
- Verbose mode (`list -v`) shows pagination details for debugging
- All commands (`list`, `delete --batch`, `cleanup`) access complete list

### Batch Delete with Wildcards
**Pattern matching using `fnmatch`:**
- Supports `*` (any characters), `?` (single char), `[abc]` (character set)
- Matches only username part of email (before `@`)
- Shows matched list before deletion for confirmation
- Supports `-y` flag to skip confirmation

### Local History
Created emails are optionally saved to `temp_emails.json` with metadata:
- email address
- rule_id (Cloudflare's "tag" field)
- description
- created_at timestamp

This file is not used by the application but serves as a local record. Failures to write history are silently ignored.

## Prerequisites for Development

1. **Python 3.6+** installed and in PATH as `python3` (Linux/macOS) or `python` (Windows)
2. **Cloudflare account** with:
   - A domain added to Cloudflare
   - Email Routing enabled for the domain
   - At least one verified destination email address
   - API token with Email Routing permissions
3. **`.env` file** created from `.env.example` with valid credentials

## Common Pitfalls

- **"缺少必需的环境变量" error**: `.env` file is missing or incomplete
- **401 errors**: Invalid or expired API token
- **403 errors**: API token lacks required permissions (needs `Zone.Email Routing Rules.Edit`)
- **Shell script not executable**: Run `chmod +x temp-email.sh temp_email.py`
- **Windows "python not found"**: Python may need to be added to PATH, or use `py` instead of `python`
- **PowerShell execution policy error**: Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` or use CMD with `.bat` file
- **Network errors (getaddrinfo failed)**: Check network connection, proxy settings, or firewall blocking Python
