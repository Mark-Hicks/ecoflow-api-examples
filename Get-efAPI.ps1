# Get EcoFlow API/MQTT Credentials & show device info
# By: Mark Hicks - 03/15/2023

# URLs
$URL       = 'https://api.ecoflow.com'
$CertPath  = '/iot-open/sign/certification'
$DevPath   = '/iot-open/sign/device/list'
$QuotaPath = '/iot-open/sign/device/quota/all'

# This is placeholder data, edit to use your API keys!
$AccessKey = '1aa2bb3cc4dd5ee6ff7aa8bb9cc10dd1'
$SecretKey = '11aa12bb13cc14dd15ee16ff17aa18bb'

Function HMAC-SHA256 ($Str, $Key) {
    $SHA     = New-Object System.Security.Cryptography.HMACSHA256
    $SHA.key = [Text.Encoding]::UTF8.GetBytes($Key)
    $Hash    = $SHA.ComputeHash([Text.Encoding]::UTF8.GetBytes($Str))
    Return ([System.BitConverter]::ToString($Hash)).Replace('-', '').toLower()
}

Function GetAPI ($Path, $Params) {
    $nonce     = Get-Random -Minimum 100000 -Maximum 999999
    $timestamp = [int64](([datetime]::UtcNow)-(get-date "1/1/1970")).TotalMilliseconds
    $Headers   = @{}
    $Headers.add('accessKey',$accessKey)
    $Headers.add('nonce',$nonce)
    $Headers.add('timestamp',$timestamp)
    $SignStr   = ($Headers.keys | sort | % {"$_=$($Headers[$_])"}) -join '&'
    if ($Params) {
        $Pstr = ($Params.keys | sort | % {"$_=$($Params[$_])"}) -join '&'
        $SignStr = "$Pstr&$SignStr"
    }
    $Sign      = HMAC-SHA256 $SignStr $SecretKey
    $Headers.add('sign',$Sign)
    iwr "$URL$Path" -Headers $Headers -Body $Params
}

"MQTT Credentials..."
$CredInfo  = GetAPI $CertPath
$Creds     = ($CredInfo.content | ConvertFrom-Json).data
$Creds | FL url, port, protocol, certificateAccount, certificatePassword

"Device List..."
$DevInfo   = GetAPI $DevPath
$Devices   = ($DevInfo.content | ConvertFrom-Json).data
$Devices | FT deviceName, sn, online

"Quota Data..."
""
$Quotas = $Devices | % {
    $QuotaInfo = GetAPI $QuotaPath @{'sn'=$($_.sn)}
    $Quota = ($QuotaInfo.content | ConvertFrom-Json).data | Select DeviceName, DeviceSN, *
	$Quota.DeviceName = $_.DeviceName
	$Quota.DeviceSN   = $_.SN
	$Quota
}
$Quotas
