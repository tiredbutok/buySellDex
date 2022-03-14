## Description
It's my attempt at creating very basic program to buy/sell tokens faster by using web3.py and availible router contracts instead of frontend AMM which often prove to be laggy. It's not to say that it guarantees that you will not get rekt... It's not a mempool bot or anything of the sorts. It just makes purchase faster by avoiding slow UI. Right now it supports only BUYING, so you still have to sell them using UI :|. Supported chains as of now are bsc, fantom and ropsten test network. You can add appropriate data to config.py file, most of EVM chains should work but some of them use different function names eg. AVAX.  
THE PURPOSE FOR THIS PROGRAM IS FOR ME TO LEARN NOT TO MAKE MONEY SO BE CAREFUL WHILE USING IT !!!!!
## Setup
### ENVIRONMENTAL VARIABLES
This program requires you to setup some environmental variables in order for you to use it. <font color="red">main.py</font> needs to know your <font color="green">PRIVATE_KEY</font> and <font color="green">SENDER_ADDRESS</font>, <font color="red">config.py</font> needs to know your <font color="green">ROPSTEN_RPC</font> api key eg. from INFURA.
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
## Disclaimer
PLEASE AVOID USING YOUR MAIN CRYPTO ACCOUT WHILE DEALING WITH THIS PROGRAM, I'M NOT A PROFESSIONAL. MAIN PURPOSE OF THIS PROGRAM IS FOR ME TO UNERSAND WEB3PY PACKAGE AND HOW ROUTER CONTRACT WORKS. I'M NOT LIABLE FOR ANY LOSS OR DAMAGE ARISING DIRECTLY OR INDIRECTLY FROM YOUR USE OF THE PROGRAM.
