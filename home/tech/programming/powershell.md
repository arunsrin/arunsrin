---
title: "Powershell"
tags:
  - powershell
  - scripting
---

# :material-powershell:{ .anim-bounce } Powershell

These notes are from **Mastering PowerShell Scripting - Fourth Edition**, by
Chris Dent.

## Discovery, Basics

`Update-Help` to get the latest docs.

`Get-help Get-Process` gets you help about the `Get-Process` command.

Very cool, you can also add a `-Examples` to specifically see a bunch of
examples :)

`Get-Command` shows all available commands, and you can use a regex like this
to filter the output:

```
Get-Command Get-*ip*
```

`Get-Alias` prints all the aliases, as always use regexes to filter, e.g.
`Get-Alias s*`. Some linux equivalents:

```
Copy-Item -> cp
Get-ChildItem -> ls
Get-Content -> cat
Get-Location -> pwd
Remove-Item -> rm
Write-Output -> cat
```

## Exercise

Create an empty file, pipe some content to it and display the result.

```
new-item helloworld.txt
add-content "this is like echo > " .\helloworld.txt    # this is wrong
get-help Add-Content -examples
add-content -value "this is like echo > " -path .\helloworld.txt # this is correct
get-content .\helloworld.txt
```

## Common parameters

Almost all commands support commonparameters like these: 

- `Debug`
- `ErrorAction`: what to do on non-terminating errors, e.g. ignore, enquire,
continue, stop
- `ErrorVariable`: variable that stores all stderr
- `InformationAction`, `InformationVariable`, `OutBuffer`, `OutVariable`:
similar to above
- `Verbose`
- `Confirm`: prompt before executing
- `PassThru`: return the same object back, e.g. `Start-Process notepad -PassThru`

More in `Get-Help about_CommonParameters`

## Providers

Specialized interfaces to a service or dataset, e.g. `Alias`, `Environment`,
`Filesystem`, `Function`, `Variable`, `Registry`, `Certificate`, `WSMan`.

More in `Get-Help about_Providers` and `Get-Help
about_<ProviderName>_Provider`.

To see all content in a provider, do this: `get-childitem environment::`

## Splatting

Sort-of like using a dict to store the cmd and args.

```powershell
$splat = @{
Name = 'explorer'
}

Get-process @splat
```

Useful for readability, breaking long lines into smaller chunks. And for
setting a conditional parameter in the dictionary and invoking the command with
it.

