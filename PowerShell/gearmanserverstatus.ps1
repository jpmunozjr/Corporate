#List of gearman servers
$GearmanServer = "SERVER"
#Count to create infinite loop
$Count = 0
#Server name for email purposes
$Hostname = (Get-WmiObject -Class Win32_ComputerSystem -Property Name).Name
#Email recipient
$To = 'EMAIL'
#Email sender
$From = "$Hostname@DOMAIN"
#Email subject line
$Subject = "$Hostname - HIDS_MBMR_listner failed to restart."
#Email server
$Server = 'MAIL_SERVER'
#Email message
$Body = @" 
            All:<br><br>
        
            $Hostname is no longer communicating with $GearmanServer.<br><br>
        
            Please log in to $Hostname and enable the HIDS_MBMR_listner task.<br><br>

            Thanks
"@

#Infinite loop
while ($Count -eq 0)
{
    #Check if gearman server is online or offline - Should run in background entire time
    $ServerStatus = Test-Connection -BufferSize 16 -Count 1 -ComputerName $GearmanServer -Quiet
    #Wait 1 second
    Start-Sleep -Seconds 1

    #If gearman server is offline
    if ($ServerStatus -eq $false)
    {
        #Stop HIDS_MBMR_listner
        Get-ScheduledTask -TaskName HIDS_MBMR_listner | Stop-ScheduledTask
    }

    #If gearman server comes back online
    elseif (($ServerStatus -eq $true) -and ((Get-ScheduledTask -TaskName HIDS_MBMR_listner).State) -ne "Running")
    {
        #Start HIDS_MBMR_listner
        Get-ScheduledTask -TaskName HIDS_MBMR_listner | Start-ScheduledTask
        #Wait 5 minutes
        Start-Sleep -Seconds 300
        #Check task status again to ensure it is running
        $SecondChance = ((Get-ScheduledTask -TaskName HIDS_MBMR_listner).State)
        #If HIDS_MBMR_listner is still inactive
        if ($SecondChance -ne "Running")
        {
            #Email IS Security group for manual intervention
            Send-MailMessage -To $To -from $From -body $Body -subject $Subject -SmtpServer $Server -BodyAsHtml

        }
    }
}