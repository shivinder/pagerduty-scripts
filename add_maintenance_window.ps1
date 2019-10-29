$url='https://api.pagerduty.com/maintenance_windows'

$headers = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
$headers.Add("Accept", 'application/vnd.pagerduty+json;version=2')
$headers.Add("Authorization", 'Token token=YourTokenHere')
$headers.Add("From",'user@email.com')

$services=@()
$body = "{
            'maintenance_window': {
                'type': 'maintenance_window',
                'start_time': '2019-11-29T20:00:00-05:00',
                'end_time': '2019-11-30T22:00:00-05:00',
                'description': 'Immanentizing the eschaton',
                'services': [
                    {
                        'id': 'P8CZXXX',
                        'type': 'service_reference'
                    }
                ]
            }

        }"

Write-Host $body

$results = Invoke-RestMethod -Uri $url -method POST -ContentType 'application/json' -Body $body -Headers $headers 