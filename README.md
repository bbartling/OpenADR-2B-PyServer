# OpenADR-PenTest-Lab
OpenADR-PenTest-Lab is a testbed for learning web app penetration testing in Open Automated Demand Response (OpenADR) systems. It provides a realistic environment for security enthusiasts to practice pen testing on a Virtual Top Node (VTN) server for demand response applications, grid-interactive efficient buildings (GEB), and OpenADR protocols.

## Web App Interface
The interface on the demand response server used to configure demand response events is made with React which then communicates to the Python backend. The Python backend runs [openleadr](https://openleadr.org/docs/) project under the hood which is a Python based OpenAdr 2.0 library.

<details>
  <summary>Web App Interface Screenshot</summary>
    ![Alt text](/images/app_gui.JPG)
</details>

## Project goals
These are some basic goals to make this into an interactive Pen test lab for demand response.
 - [x] create basic Python Virtual Top Node (VTN) app
 - [x] create basic React based interface for the GUI
 - [x] test VTN and React interface with a `localhost` OpenADR client
 - [x] make a communications diagram for project
 - [ ] make a login page for the VTN server
 - [ ] deploy on the internet and test remote OpenAdr client
 - [ ] start the fun stuff and make some Pen Testing script : )

 ## Communications schematic
 <details>
  <summary>Communications Diagram</summary>
    ![Alt text](/images/schematic.JPG)
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