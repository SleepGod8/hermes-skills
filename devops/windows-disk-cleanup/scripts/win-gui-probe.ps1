# win-gui-probe.ps1 -- background GUI probing/clicking for Windows apps (no computer_use tool needed)
# Usage:
#   -Action list  -Pid_ 1234                                  enumerate visible windows of a pid
#   -Action shot  -Hwnd 1116436 -Out 'C:\tmp\win.png'          PrintWindow one window (works even if covered)
#   -Action click -Hwnd 1116436 -X 1206 -Y 441 [-Button right]  PostMessage click at CLIENT coords
#   -Action top   -Hwnd 1116436                                HWND_TOPMOST (fixes ignored clicks)
#   -Action untop -Hwnd 1116436                                restore z-order
# Rules baked in (see SKILL.md):
#   * SetProcessDpiAwarenessContext(-4) FIRST, else GetWindowRect and pixels disagree on 125-150% scaling
#   * never CopyFromScreen for a covered window: you capture the covering window and misread the UI
#   * Qt menus are separate top-level windows -> enumerate by pid, then PrintWindow the popup's own hwnd
#   * click coords = window-local coords - (clientOrigin - windowOrigin); shot prints both origins
#   * ASCII-only source: PowerShell 5.1 reads BOM-less .ps1 as GBK and breaks on non-ASCII literals
param(
  [ValidateSet('list','shot','click','top','untop')][string]$Action = 'list',
  [long]$Hwnd = 0,
  [int]$Pid_ = 0,
  [int]$X = -1,
  [int]$Y = -1,
  [ValidateSet('left','right')][string]$Button = 'left',
  [string]$Out = ''
)
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public class GWin {
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr v);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr h, ref POINT p);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint flags);
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr after, int x, int y, int cx, int cy, uint flags);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr p);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern int GetWindowTextW(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern int GetClassNameW(IntPtr h, StringBuilder s, int n);
  public delegate bool EnumProc(IntPtr h, IntPtr p);
  public struct RECT { public int Left, Top, Right, Bottom; }
  public struct POINT { public int X, Y; }
}
"@
try { [void][GWin]::SetProcessDpiAwarenessContext([IntPtr](-4)) } catch { [void][GWin]::SetProcessDPIAware() }
[void][GWin]::SetProcessDPIAware()

function Show-Windows([int]$targetPid) {
    $script:found = @()
    $cb = [GWin+EnumProc]{
        param($wh, $l)
        $wp = 0
        [void][GWin]::GetWindowThreadProcessId($wh, [ref]$wp)
        if (($targetPid -eq 0 -or $wp -eq $targetPid) -and [GWin]::IsWindowVisible($wh)) {
            $sb = New-Object System.Text.StringBuilder 256
            [void][GWin]::GetWindowTextW($wh, $sb, 256)
            $cn = New-Object System.Text.StringBuilder 256
            [void][GWin]::GetClassNameW($wh, $cn, 256)
            $r = New-Object GWin+RECT
            [void][GWin]::GetWindowRect($wh, [ref]$r)
            $script:found += [PSCustomObject]@{
                H = $wh; Class = $cn.ToString(); Title = $sb.ToString()
                L = $r.Left; T = $r.Top; R = $r.Right; B = $r.Bottom
            }
        }
        return $true
    }
    [void][GWin]::EnumWindows($cb, [IntPtr]::Zero)
    $script:found | ForEach-Object {
        "WIN h={0} class={1} rect=({2},{3},{4},{5}) size={6}x{7} title={8}" -f `
            $_.H, $_.Class, $_.L, $_.T, $_.R, $_.B, ($_.R-$_.L), ($_.B-$_.T), $_.Title
    }
}

$h = [IntPtr]$Hwnd
switch ($Action) {
  'list' { Show-Windows $Pid_ }
  'top' {
    [void][GWin]::SetWindowPos($h, [IntPtr](-1), 0,0,0,0, 0x0003)
    Write-Output "TOPMOST set h=$Hwnd"
  }
  'untop' {
    [void][GWin]::SetWindowPos($h, [IntPtr](-2), 0,0,0,0, 0x0003)
    Write-Output "TOPMOST cleared h=$Hwnd"
  }
  'click' {
    $lp = [IntPtr](($Y -shl 16) -bor ($X -band 0xFFFF))
    [void][GWin]::PostMessage($h, 0x0200, [IntPtr]::Zero, $lp)
    Start-Sleep -Milliseconds 120
    if ($Button -eq 'right') {
      [void][GWin]::PostMessage($h, 0x0204, [IntPtr]2, $lp); Start-Sleep -Milliseconds 90
      [void][GWin]::PostMessage($h, 0x0205, [IntPtr]::Zero, $lp)
    } else {
      [void][GWin]::PostMessage($h, 0x0201, [IntPtr]1, $lp); Start-Sleep -Milliseconds 90
      [void][GWin]::PostMessage($h, 0x0202, [IntPtr]::Zero, $lp)
    }
    Start-Sleep -Milliseconds 1000
    Write-Output "POSTED $Button click client=$X,$Y h=$Hwnd"
    if ($Pid_ -gt 0) { Show-Windows $Pid_ }
  }
  'shot' {
    $r = New-Object GWin+RECT
    [void][GWin]::GetWindowRect($h, [ref]$r)
    $p = New-Object GWin+POINT
    [void][GWin]::ClientToScreen($h, [ref]$p)
    $w = $r.Right - $r.Left; $hh = $r.Bottom - $r.Top
    $bmp = New-Object System.Drawing.Bitmap($w, $hh)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $hdc = $g.GetHdc()
    [void][GWin]::PrintWindow($h, $hdc, 2)
    $g.ReleaseHdc($hdc); $g.Dispose()
    $bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
    Write-Output "SHOT $Out (${w}x${hh}) windowOrigin=($($r.Left),$($r.Top)) clientOrigin=($($p.X),$($p.Y))"
  }
}
