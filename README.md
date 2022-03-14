## Setup
### Virtual Env
It's best to create virtual env instead of istalling dependencies globally.  
Create python venv:
~~~
python3 -m venv myVenv
~~~
Activate virtual env (linux):
~~~
source myVenv/bin/activate
~~~
### Install requirements
After activating virtual env install all requirements:
~~~
pip3 install -r requirements.txt
~~~
### Run program
~~~
python3 main.py <chain> [-f]
~~~
#### Description
&nbsp;&nbsp;&nbsp;&nbsp;&lt;chain> - as of now bsc, ftm, ropsten  
&nbsp;&nbsp;&nbsp;&nbsp;[-f] - use when you want to buy instantly after defining gas price
#### Example
~~~
python3 main.py bsc -f
~~~