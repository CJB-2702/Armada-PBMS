Goal:
Allow a user to request a dispatch
Provide a friendly interface for the dispatcher to select a vehicle
dispatch a vehicle, reject the dispatch, contract out the dispatch, Reimburse the employee for their own dispatch

USERS:
- Requester
	- make it easy to fill out the forms to request a dispatch and recieve emails with status updates
- Dispatcher
	- easily view all dispatch requests and current dispatches for an asset type and select the best option to dispatch
	- 
- Fleet manager
	- View statistics about dispatches and so forth



User requests Dispatch:
a factory class creates an event  with a dispatch header document
- Generic dispatch form
	 - Dates Required
	 - Number of people using the dispatch
		 - optionally list names, no database just a text list or json
	 - specific asset request
	 - Estimated meter usage
	 - major location select
	 - notes
	 - Asset type
	 - Asset subclass requested (string)
		 - Light transport
			 - ATV's golf carts electric bikes
		 - Personnel Transport
			 - Passenger Vehicles, sprinter vans
		 - Heavy Duty Transport
			 - Transport that requires special certification or training ex school bus , military trucks etc
		 - Equipment Transport
			 - Trucks f150s f250s etc 
		 - Heavy Duty Equipment Transport
			 - Trucks that require certification or training, ex tow trucks cranes etc
		 - Other
			 - fork lifts, aircraft tows, lawn mowers
	 - Dispatch Subclass requested (string)
		 - onsite
			 - never leaves facilities
		 - local
			 - travel generally within a 50 mile range
		 - regional 
			 - travel between 1 and 8 hours  or 50 and 500
		 - interstate
			 - Travel greater than 8 hours
		 - continental 
			 - Travel outside of the continent
	 - 
Dispatcher reviews open requests
- dispatcher has a dispatch queue and an asset resource calendar
	- Dispatch queue on left 1/3  resource calender is 2/3 of screen
- dispatcher selects a request, 
	- details expand
	- dates become highlighted
	- free assets filter to top
	- dispatcher can filter by 
		- location 
		- model 
		- equipment id
		- status
	- onclick last maintnence event title and date is listed
- dispatcher selects an action
	- reserve
	- reject
	- contract
		- dispatch is set to contracted status
		- contract form is generated
			- company, cost  etc
	- Reimbursement
		- reimbursement form is generated, from account to account and how much and why

Dispatch can be edited
	starting later or finishing earlier does not require approval, a notification is sent to dispatcher
	starting earlier or finishing later generates an edit request
	dispatcher must edit the request
	dispatcher can change status at will


fleet manager:
 reviews dashboard and can see the dispatch calendar






