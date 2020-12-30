# Generate the incidents report from a PagerDuty Account

## Requirements

* A global REST API key from your PagerDuty account

## Steps to run the script

The script is written in python 3.9. It would be possible to run it in any 3.x version of Python language. 

1) Change directory to the script directory and create a virtual environment using the following command -> `python3 -m venv env`
2) Activate the virtual environment with this command -> `. env/bin/activate`
3) Install the dependencies by running -> `pip install -r requirements.txt`
4) Run the script
5) Deactivate the pythin virtual environment by running -> `deactivate`, or simply close your terminal

## Syntax to run the script

```
python get_incidents_report.py --api-key YOUR-API-KEY-HERE
```

## Optional arguments you may supply to generate a more specialised report

### --service-ids

Supply this argument to generate the report for the supplied Service ID only. You may supply more than one Service ID using comma as a seperator. 

Example of generating an incidents report for a single Service ID

```
python get_incidents_report.py --api-key YOUR-API-KEY-HERE --service-ids PXXXXXX
```

Example of generating an incidents report for multiple Service IDs

```
python get_incidents_report.py --api-key YOUR-API-KEY-HERE --service-ids PXXXXX1,PXXXXX2
```
