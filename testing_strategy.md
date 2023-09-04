##FIT2107 Assignment 2 Testing Strategy Document

###Team - Workshop02 Team8
* Shang-Fu Tsou 

* Aritro Dutta

* En Xin Wong


##Base
The goal of this project is to develop a calendar program using the Google Calendar API. Base on specifications, a set 
of functionalities will be implemented and tested via the practice of Test Driven Development. The program will have
access to the user's Google calendar, from which, the user can then conduct similar calendar functionalities through
the processing console.

This document outlines the testing and development processes that will be conducted by all team member.


##Testing Approach
Since this project will be implemented mainly through modular programming, unit tests will be conducted to test discrete
functionalities.

Test cases will be written through a combination of whitebox and blackbox testing as outlined in the following sections.

<table>
    <tr>
        <td>
            Whitebox Testing
        </td>
        <td>
            Statement Coverage
            <p></p>
            Branch Coverage
            <p></p>
            Condition Coverage
            <p></p>
        </td>
    </tr>
    <tr>
        <td>
            Blackbox Testing
        </td>
        <td>
            Category Partitioning
            <p></p>
            Equivalence Partitioning
            <p></p>
            Boundary Value Analysis
        </td>
    </tr>
</table>

As blackbox testing is not within the scope of this project/assignment, it is not formally documented. However, due to
the nature of the implementation being console-based, certain test cases are first planned as blackbox tests simulating
the process of providing inputs to the program. If applicable, Unittest test cases will then be written to simulate that
process. A general outline of the testing & development process is outlined as such:
1. Understand the API documentation for the functionality to be implemented.
2. Define appropriate functions that may be required.
3. Write basic unit tests that will test the validity of desired implementation.
   * At this stage, the test cases written will be very simple, such as testing if the API method has been called.
4. Begin implementation of the functionalities.
5. Refine test cases/suites for more in-depth testings based on implementation.
6. If applicable, generate blackbox test cases through running the program itself with boundary values and inputs that
   could potentially break the program.
   1. Replicate these test cases in unit testing.
      * This is mainly applied with creating a new event, which requires many user inputs, each with their own set of
        conditions and boundary values.
   2. Refine implementation 
7. Fix bugs or implementation if the pipeline fails.

Members will try to follow the process outlined above.

The main focus of the unit tests will be to reach the target branch and statement coverages. This is done by covering 
all boundary values for different categories/input fields, and ensuring each branch is ran at least once.

A major consideration taken in when writing the unittests, is that the program is console-based as mentioned previously.
Because of such implementation, many tests requiring user inputs can be done sequentially, particularly during user input
validation. This is important because multiple fields can be independently tested within the same test cases with patching 
and side effects as each input field must be validated before moving onto the next.

MC/DC will be used when the number of test cases need to be reduced for decision coverage. However, after completing the
project, MC/DC was not very applicable due to the nature of the implementation and how each code branch is constructed.


###Testing Tools
During the testing process outlined above, the following tools will be used.

####Unittest
The main testing framework used is unittest, which is a standard python module. From which, associated modules such as
MagicMock and patch will be utilized. Unittesting will be used to test individual functions and modules in the 
program.

####Mocking
Mocking will be used to simulate the API, API calls, as well as certain implemented functions to assist in testing the 
code functionalities and allowing different branch coverage testings to be conducted, without needing the real API and
access to a Google calendar.

####Others
The modules **sys** and **StringIO** will also be used, along with **patching** and **side effects** to detect console
outputs to test the program's behaviors and responses.

####Continuous Integration
Continuous Integration will run upon pushing commits to the GitLab repository.

####Coverage.py
To perform coverage testing, **coverage.py** is installed to calculate the percentage of branch coverage the unittests
provide.

##Risk Management Plan
<table>
    <tr>
        <td>
            Risk
        </td>
        <td>
            Severity
        </td>
        <td>
            Likelihood
        </td>
        <td>
            Mitigation Strategy
        </td>
    </tr>
    <tr>
        <td>
            Member's device breaks
        </td>
        <td>
            4/5
        </td>
        <td>
            2/5
        </td>
        <td>
            Exercise care when using own devices and refrain from exposing said device to potential sources of damage.
        </td>
    </tr>
    <tr>
        <td>
            Member falls ill
        </td>
        <td>
            3~4/5
        </td>
        <td>
            3/5
        </td>
        <td>
            Practice good hygiene and dress to stay warm during cold weather.
        </td>
    </tr>
    <tr>
        <td>
            Merge conflicts when pushing to git
        </td>
        <td>
            3/5
        </td>
        <td>
            4/5
        </td>
        <td>
            Let teammates know what's being worked on and push sequentially to avoid these conflicts
        </td>
    </tr>
</table>