#List of admin groups to pull users from
$ADGroupNames = "NAME1", "NAME2"

#Cycles through user groups
$Output = foreach($ADGroupName in $ADGroupNames) 
{
    #Get group members, select SamAccountName, and change to lowercase
	(Get-ADGroupMember $ADGroupName -Recursive | Select-Object -ExpandProperty SamAccountName).ToLower()
}

#Output unique names to an ASCII-encoded text file
$Output | Sort-Object -Unique | Out-File \\some\text\file.txt -Encoding ascii