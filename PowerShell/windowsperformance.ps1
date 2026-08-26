#################
### Variables ###
#################

#List of windows servers
$windows_servers = @("SERVER1","SERVER2")

###############
### Program ###
###############

#Cycle through windows servers

foreach ($server in $windows_servers)
{
    try {
        $computer_cpu = (Get-WmiObject -Class win32_processor | Measure-Object -property LoadPercentage -Average).Average

        $computer_hdd = Get-WmiObject -ComputerName $server -Class win32_logicaldisk -Filter "DeviceID='E:'"
        $hdd = ((($computer_hdd.Size - $computer_hdd.FreeSpace)*100)/ $computer_hdd.Size)
        $round_hdd = [math]::Round($hdd,2)

        $computer_ram = Get-WmiObject -ComputerName $server -Class win32_operatingsystem
        $ram = ((($computer_ram.TotalVisibleMemorySize - $computer_ram.FreePhysicalMemory)*100)/ $computer_ram.TotalVisibleMemorySize)
        $round_ram = [math]::Round($ram, 2)

        $date = Get-Date

        #Write server stats to log file
        "$date , $server , $computer_cpu , $round_hdd , $round_ram" | Out-File -filepath \\some\log\file.log -Append -Encoding ascii
    }
    catch {
        Write-Output "Failed to complete on $server."
    }
}