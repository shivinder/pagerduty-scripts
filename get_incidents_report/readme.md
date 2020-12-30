# Generate the incidents report from a PagerDuty Account

## Requirements

* A global REST API key from your PagerDuty account

## Steps to run the script

The script is written in python 3.9. It would be possible to run it in any 3.x version of Python language. 

1) Change directory to the script directory and create a virtual environment using the following command -> `python3 -m venv env`
2) Activate the virtual environment with this command -> `. env/bin/activate`
3) Install the dependencies by running -> `pip install -r requirements.txt`
4) Run the script

## Syntax to run the script

```
python get_incidents_report.py --api-key YOUR-API-KEY-HERE
```