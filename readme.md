# CrisisProfile

The mission of CrisisProfile is to help individuals and groups prevent, de-escalate, and stabilize after crises.

## Running CrisisProfile locally

### Initial prep

* Setup a Ngrok.io account with subdomain
* Setup an Auth0 account with two connections
* Add evars for Auth0

### Commands for running each time

Command for starting Django ``cd crisisprofile; nanobox run python manage.py runserver 0.0.0.0:8000``  
Command for starting Ngrok.io ``cd; ./ngrok http --subdomain=[YOUR NGROK SUBDOMAIN] crisisprofile.local:8000``  

## Profile data structure

* identity
  * entity_type
  * first_name
  * middle_name
  * last_name
  * US_state_ID
    * state ``abbreviation``
    * id
  * emails ``list``  
  * SSN
  * birthdate
