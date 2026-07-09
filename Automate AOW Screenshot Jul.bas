Attribute VB_Name = "Module1"
'=============================================================
' MODULE: FilterInPlace_And_Screenshot_Fixed
' COMPATIBLE: Mac & Windows
' SHEET: "Timeline in Jun"
' FILTER: Column F (Supervisor), rows 6-91
' OUTPUT: One PNG per supervisor, sorted alphabetically
' DEBUG: Prints DT list & Dayoff count to Immediate Window
'=============================================================

Option Explicit

'-----------------------------------------------------------
' Helper: Native folder picker (Mac & Windows)
'-----------------------------------------------------------
Function SelectSaveFolder() As String
    #If Mac Then
        Dim script As String
        Dim folderPath As String
        script = "set chosenFolder to choose folder with prompt ""Select folder to save screenshots:"" " & vbNewLine & _
                 "return POSIX path of chosenFolder"
        On Error Resume Next
        folderPath = MacScript(script)
        If Err.Number <> 0 Then folderPath = ""
        On Error GoTo 0
        If folderPath <> "" And Right(folderPath, 1) <> "/" Then folderPath = folderPath & "/"
        SelectSaveFolder = folderPath
    #Else
        Dim fd As FileDialog
        Set fd = Application.FileDialog(msoFileDialogFolderPicker)
        If fd.Show = -1 Then SelectSaveFolder = fd.SelectedItems(1) & "\" Else SelectSaveFolder = ""
    #End If
End Function

'-----------------------------------------------------------
' MAIN
'-----------------------------------------------------------
Sub Run_the_Screenshot()

    Dim ws           As Worksheet
    Dim saveFolder   As String
    Dim supName      As Variant
    Dim captureRange As Range
    Dim chartObj     As ChartObject
    Dim imgPath      As String
    Dim safeName     As String
    Dim i            As Long
    Dim j            As Long
    Dim tempName     As String
    Dim alreadyAdded As Boolean
    Dim existing     As Variant
    Dim logFile      As Integer

    ' --- Dayoff related ---
    Dim todayCol     As Long
    Dim dayoffCount  As Variant
    Dim rngHeader    As Range
    Dim foundCell    As Range

    ' --- DT collection variables ---
    Dim dtList       As String
    Dim dtCollection As Collection
    Dim dtVal        As String
    Dim dtItem       As Variant
    Dim dtAdded      As Boolean

    ' --- Sorting variables ---
    Dim supervisors  As Collection
    Dim supArray()   As Variant
    Dim tempSup      As Variant

    Const WS_NAME    As String = "Screenshot"   ' ? Change if needed
    Const SUP_COL    As Long = 6                     ' Column F
    Const DT_COL     As Long = 11                    ' Column K
    Const FIRST_ROW  As Long = 6
    Const LAST_ROW   As Long = 91
    Const HEADER_ROW As Long = 4                     ' Row containing dates
    Const DAYOFF_ROW As Long = 92                   ' Row with dayoff counts
    Const FILTER_ROW As Long = 6
    Const FIELD_NUM  As Long = 6

    ' --- Ask user where to save ---
    saveFolder = SelectSaveFolder()
    If saveFolder = "" Then
        MsgBox "No folder selected. Macro cancelled.", vbExclamation
        Exit Sub
    End If

    Set ws = ThisWorkbook.Sheets(WS_NAME)

    ' --- Find today's date column in row 4 ---
    Set rngHeader = ws.Rows(HEADER_ROW)
    Set foundCell = rngHeader.Find(What:=Date, LookIn:=xlFormulas, LookAt:=xlWhole)
    If Not foundCell Is Nothing Then
        todayCol = foundCell.Column
    Else
        MsgBox "Today's date (" & Date & ") not found in row " & HEADER_ROW & ". Dayoff count will be omitted.", vbExclamation
        todayCol = 0
    End If

    ' --- 1. Collect unique supervisors (rows 6-136) ---
    Set supervisors = New Collection
    For i = FIRST_ROW To LAST_ROW
        tempName = Trim(CStr(ws.Cells(i, SUP_COL).Value))
        If tempName <> "" And tempName <> "False" Then
            alreadyAdded = False
            For Each existing In supervisors
                If CStr(existing) = tempName Then
                    alreadyAdded = True
                    Exit For
                End If
            Next existing
            If Not alreadyAdded Then supervisors.Add tempName
        End If
    Next i

    If supervisors.Count = 0 Then
        MsgBox "No supervisors found in column F (rows 6-261).", vbExclamation
        Exit Sub
    End If

    ' --- 2. Convert Collection to Array and sort alphabetically (A?Z) ---
    ReDim supArray(1 To supervisors.Count)
    For i = 1 To supervisors.Count
        supArray(i) = supervisors(i)
    Next i

    ' Bubble Sort (case-insensitive)
    For i = 1 To UBound(supArray) - 1
        For j = i + 1 To UBound(supArray)
            If StrComp(supArray(i), supArray(j), vbTextCompare) > 0 Then
                tempSup = supArray(i)
                supArray(i) = supArray(j)
                supArray(j) = tempSup
            End If
        Next j
    Next i

    Application.DisplayAlerts = False
    Application.ScreenUpdating = False

    ' --- Clear the Immediate Window (optional) ---
    ' Debug.Print String(80, "-") & " Starting Macro " & String(80, "-")

    ' --- 3. Loop through sorted array ---
    For i = 1 To UBound(supArray)
        supName = supArray(i)

        ' --- Collect unique DT values for this supervisor ---
        Set dtCollection = New Collection
        For j = FIRST_ROW To LAST_ROW
            If Trim(CStr(ws.Cells(j, SUP_COL).Value)) = CStr(supName) Then
                dtVal = Trim(CStr(ws.Cells(j, DT_COL).Value))
                If dtVal <> "" And dtVal <> "False" Then
                    dtAdded = False
                    For Each dtItem In dtCollection
                        If CStr(dtItem) = dtVal Then
                            dtAdded = True
                            Exit For
                        End If
                    Next dtItem
                    If Not dtAdded Then dtCollection.Add dtVal
                End If
            End If
        Next j

        ' Build DT string
        dtList = ""
        For Each dtItem In dtCollection
            If dtList = "" Then
                dtList = CStr(dtItem)
            Else
                dtList = dtList & "-" & CStr(dtItem)
            End If
        Next dtItem

        ' --- ? DEBUG: Print DT list to verify it belongs to this supervisor ? ---
        Debug.Print "Supervisor: " & supName & "  |  DTs: " & dtList

        ' --- 4. Apply filter ---
        If ws.AutoFilterMode Then ws.AutoFilterMode = False
        ws.Range("A6:AY6").AutoFilter Field:=FIELD_NUM, Criteria1:=CStr(supName)
        
        ' Ensure filter is applied on Mac
        On Error Resume Next
        ws.AutoFilter.ApplyFilter
        On Error GoTo 0

        ' --- 5. ? FORCE RECALCULATION (critical for row 114) ? ---
        Application.CalculateFull           ' Full recalc of all workbooks
        ' Explicitly recalc the dayoff cell (belt & suspenders)
        If todayCol > 0 Then
            ws.Range(ws.Cells(DAYOFF_ROW, todayCol), ws.Cells(DAYOFF_ROW, todayCol)).Calculate
        End If
        
        Application.ScreenUpdating = True
        DoEvents
        Application.Wait Now + TimeValue("00:00:02")   ' Wait for rendering

        ' --- 6. Get dayoff count for today ---
        dayoffCount = ""
        If todayCol > 0 Then
            On Error Resume Next
            dayoffCount = ws.Cells(DAYOFF_ROW, todayCol).Value
            If IsNumeric(dayoffCount) Then
                dayoffCount = Round(dayoffCount, 0)
            Else
                dayoffCount = ""
            End If
            On Error GoTo 0
            
            ' --- ? DEBUG: Print dayoff count to verify it belongs to this supervisor ? ---
            Debug.Print "Dayoff for " & supName & ": " & dayoffCount
            Debug.Print "----------------------------------------"
            
            If dayoffCount <> "" And dayoffCount <> 0 Then
                dayoffCount = "_Check-In=" & dayoffCount
            Else
                dayoffCount = ""
            End If
        End If

        ' --- 7. Take screenshot ---
        Set captureRange = ws.Range("A2:AU99")
        captureRange.CopyPicture Appearance:=xlScreen, Format:=xlPicture

        ' --- 8. Create temp chart and paste ---
        Set chartObj = ws.ChartObjects.Add(Left:=0, Top:=0, Width:=captureRange.Width, Height:=captureRange.Height)
        chartObj.Activate
        DoEvents
        Application.Wait Now + TimeValue("00:00:01")
        chartObj.Chart.Paste
        DoEvents
        Application.Wait Now + TimeValue("00:00:02")

        ' --- 9. Build safe filename (including dayoff) ---
        safeName = CStr(supName) & "_" & dtList & dayoffCount
        safeName = Replace(safeName, "/", "-")
        safeName = Replace(safeName, "\", "-")
        safeName = Replace(safeName, ":", "-")
        safeName = Replace(safeName, "*", "-")
        safeName = Replace(safeName, "?", "-")
        safeName = Replace(safeName, """", "-")
        safeName = Replace(safeName, "<", "-")
        safeName = Replace(safeName, ">", "-")
        safeName = Replace(safeName, "|", "-")

        imgPath = saveFolder & safeName & ".png"

        ' --- 10. Export PNG ---
        On Error Resume Next
        chartObj.Chart.Export FileName:=imgPath, FilterName:="PNG"
        If Err.Number <> 0 Then
            MsgBox "Failed to export: " & imgPath & vbCrLf & "Error: " & Err.Description, vbCritical
            Err.Clear
        End If
        On Error GoTo 0

        ' --- 11. Clean up chart ---
        chartObj.Delete

        ' --- 12. Log the mapping ---
        On Error Resume Next
        logFile = FreeFile
        Open saveFolder & "supervisor_list.txt" For Append As #logFile
        Print #logFile, "FILE: " & safeName & ".png  |  SUPERVISOR: " & CStr(supName) & "  |  DT: " & dtList & "  |  DAYOFF: " & dayoffCount
        Close #logFile
        On Error GoTo 0

    Next i

    ' --- Clear filter and finish ---
    If ws.AutoFilterMode Then ws.AutoFilterMode = False
    Application.DisplayAlerts = True
    Application.ScreenUpdating = True

    MsgBox "Done! " & UBound(supArray) & " screenshots saved to:" & vbCrLf & saveFolder, _
           vbInformation, "Screenshot Complete"

End Sub

