---
title: "Windows"
tags:
  - tech
  - windows
  - sysadmin
---

# :material-microsoft-windows:{ .anim-bounce } Windows

## Change a wireless network to Private

```powershell
  Get-NetConnectionProfile
  # Note the InterfaceIndex here
  Set-NetConnectionProfile -InterfaceIndex <id>  -NetworkCategory Private
```

