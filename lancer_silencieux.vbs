' Lance l'application sans afficher de fenêtre console (cmd noire).
' Utilisé par le raccourci créé sur le Bureau.
' Nécessite que lancer_app.bat ait déjà été exécuté une fois (pour créer
' l'environnement virtuel "venv" et installer les dépendances).

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

strScriptPath = WScript.ScriptFullName
strDir = fso.GetParentFolderName(strScriptPath)

pythonwPath = strDir & "\venv\Scripts\pythonw.exe"

If fso.FileExists(pythonwPath) Then
    WshShell.CurrentDirectory = strDir
    WshShell.Run """" & pythonwPath & """ main.py", 0, False
Else
    MsgBox "L'environnement de l'application n'est pas encore installé." & vbCrLf & vbCrLf & _
           "Lance d'abord 'lancer_app.bat' une fois (double-clic) pour l'installation initiale.", _
           vbExclamation, "Google Maps Lead Scraper"
End If
