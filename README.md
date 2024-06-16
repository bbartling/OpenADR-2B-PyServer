# OpenADR-2B-PyServer
OpenADR-2B-PyServer is a free, open-source, and secure implementation of an OpenADR 2.0B server written in Python. Utilizing the OpenLEADR library, this project aims to provide a robust and reliable platform for Automated Demand Response (ADR) solutions. (PROJECT UNDER ACTIVE DEVELOPMENT)

## Security
Security is a top priority for OpenADR-2B-PyServer. The server uses HTTPS for encrypted communication and JWT for the web app GUI. VENs follow the OpenADR protocol and authenticate by device name per OPENLEADR.

## Acknowledgments
This project uses the [OpenLEADR](https://openleadr.org/) library for OpenADR 2.0B communication

Key Features
* **OpenADR 2.0B Specification Compliance**: Adheres to the OpenADR 2.0B standard via OPENLEADR, ensuring compatibility with a wide range of VEN (Virtual End Node) devices.
* **Secure Communication**: Implements HTTPS for secure communication between the VTN (Virtual Top Node) server, ADR app user, and VEN devices.
* **MIT Licensed**: Distributed under the MIT license, allowing for free use, modification, and distribution.
* **Scalability**: Designed to handle multiple VEN connections efficiently, making it suitable for both small-scale and large-scale ADR deployments.
* **Easy to Use**: Provides a straightforward setup process and comprehensive documentation to get you started quickly.

## Web App GUI
At the moment the web app supports OpenADR 2.0b `SIMPLE`, `ELECTRICITY_PRICE`, and `LOAD_DISPATCH` from web app GUI with drop down menu items. 
Per OpenADR spec `SIMPLE` signal can either be a `0,1,2 or 3`, `ELECTRICITY_PRICE` is a selectable kWh/Hr, and `LOAD_DISPATCH` at the moment is a selectable kW power setpoint for the building to maintain. All signals have a `duration` in minutes `start time` menu selection in UTC time zone to configure the ADR event. Also as demonstrated below are pop up alerts the web app supports for misconfigurations of VEN or ADR events.

<details>
  <summary>Web App Interface Screenshot</summary>

![Alt text](/images/app_gui.JPG)
![Alt text](/images/app_gui2.JPG)
![Alt text](/images/add_remove_events.JPG)
![Alt text](/images/ven_status.JPG)
</details>

## Ven Status
The VEN status shows all configured VENs on the VTN server and will display the last report value, engineering units, and time stamp of last check-in to the VTN server. The connection quality metric measures how consistently a VEN (Virtual End Node) checks in with the VTN (Virtual Top Node) and is calculated as a percentage reflecting the reliability of the VEN’s communication. This metric is based on the intervals between successive reports sent by the VEN. Each check-in timestamp is recorded in a deque that stores the last N check-in times. The intervals between these check-ins are calculated, and if they are within an expected threshold (e.g., 10 seconds, with a maximum acceptable interval of 20 seconds), they are considered valid. The connection quality is then computed as the ratio of valid intervals to the total number of intervals, expressed as a percentage.
```bash
Connection Quality = ( Number of Valid Intervals / Total Number of Intervals ) × 100
```

## Project goals
These are some basic goals to make this into an interactive Pen test lab for demand response.
 - [x] create basic Python Virtual Top Node (VTN) app
 - [x] create basic React based interface for the GUI
 - [x] test VTN and React interface with a `localhost` OpenADR multipe client VEN sim
 - [x] make a communications diagram for project
 - [x] add to GUI features for VEN client off/online status and last meter reading value
 - [x] add to GUI feature create a single event for multiple VENs
 - [ ] make a login page for the VTN server
 - [ ] add Docker container support
 - [ ] deploy on the internet and test remote OpenAdr client
 - [ ] deploy on open sourced bug bounty program for research purposes on making ADR servers most secure as possible

## Communications schematic
<details>
  <summary>Communications Diagram</summary>


![Alt text](/images/schematic.png)
</details>

## Contributing
Please submit a git issue or discussion on tips, tricks, and best practices...this project is to learn Web App pen testing which is a new avenue for me to venture down.

## License
MIT License

Copyright (c) 2024 Ben Bartling

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

ADDITIONAL CYBERSECURITY NOTICE: Users are encouraged to apply the highest level of cybersecurity, OT, IoT, and IT measures when using this software. The authors and copyright holders disclaim any liability for cybersecurity breaches, mechanical equipment damage, financial damage, or loss of life arising from the use of the Software. Users assume full responsibility for ensuring the secure deployment and operation of the Software in their environments.