# Windows Desktop Shortcut for OpenCode

Create a `.lnk` shortcut via PowerShell (works in Git Bash / MSYS):

```powershell
$ws = New-Object -ComObject WScript.Shell
$shortcut = $ws.CreateShortcut('C:\Users\<USERNAME>\Desktop\OpenCode.lnk')
$shortcut.TargetPath = 'E:\ai1\opencode-desktop\opencode.exe'
$shortcut.WorkingDirectory = 'E:\ai1\opencode-desktop'
$shortcut.Description = 'OpenCode Desktop'
$shortcut.Save()
```

In Hermes terminal (bash):
```bash
powershell -Command "
\$ws = New-Object -ComObject WScript.Shell
\$shortcut = \$ws.CreateShortcut('C:\\Users\\80704\\Desktop\\OpenCode.lnk')
\$shortcut.TargetPath = 'E:\\ai1\\opencode-desktop\\opencode.exe'
\$shortcut.WorkingDirectory = 'E:\\ai1\\opencode-desktop'
\$shortcut.Save()
Write-Output 'Shortcut created'
"
```

## Notes
- Desktop app and CLI share `~/.local/share/opencode/auth.json`
- API key must be set as Windows User env var for desktop app to see it:
  ```powershell
  [Environment]::SetEnvironmentVariable('DEEPSEEK_API_KEY', 'sk-...', 'User')
  ```
- May need logout/login for env var to take effect in GUI apps
