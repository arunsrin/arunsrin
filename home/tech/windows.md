---
title: "Windows"
icon: ":material-microsoft-windows:{ .anim-bounce }"
tags:
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

