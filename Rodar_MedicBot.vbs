' Abre o MedicBot como Administrador, sem janela de terminal.
' Ao clicar, o Windows pede "Deseja permitir?" uma vez; depois o MedicBot abre.

Set fso = CreateObject("Scripting.FileSystemObject")
pasta = fso.GetParentFolderName(WScript.ScriptFullName)
' ShellExecute com "runas" = executa como administrador (pede UAC)
' 0 = não mostrar janela de console
CreateObject("Shell.Application").ShellExecute "pythonw", "medicbot.py", pasta, "runas", 0
