$policy = net accounts

$result = @{
    min_length = ($policy | Select-String "Minimum password length").ToString().Split(":")[1].Trim()
    max_age_days = ($policy | Select-String "Maximum password age").ToString().Split(":")[1].Trim().Split(" ")[0]
    min_age_days = ($policy | Select-String "Minimum password age").ToString().Split(":")[1].Trim().Split(" ")[0]
    lockout_threshold = ($policy | Select-String "Lockout threshold").ToString().Split(":")[1].Trim()
}

$result | ConvertTo-Json
