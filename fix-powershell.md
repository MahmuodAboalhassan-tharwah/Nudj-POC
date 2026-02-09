# Fix PowerShell Execution Policy

The error "running scripts is disabled" means PowerShell execution policy is too restrictive.

## Quick Fix (Recommended)

Run this command in PowerShell **as Administrator**:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then press `Y` to confirm.

## Or Use This Workaround (No Admin Required)

Instead of `npm run dev`, use:

```powershell
node node_modules/vite/bin/vite.js
```

Or:

```cmd
# Use CMD instead of PowerShell
cmd
npm run dev
```

## Verify Fix

```powershell
Get-ExecutionPolicy -List
# Should show RemoteSigned for CurrentUser
```
