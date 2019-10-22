## Synopsis

This is study project from [dvmn.org](http://dvmn.org).

## Motivation

Do you like XKCD comics? This script helps you to share these comics with your vk's public subscribers in one line

## Installation

This project is working on `python => 3.6`

Before execute script install packages from ```requirements.txt```

```pip3 install -r requirements.txt``` 

## How To Use

Before run script add this Environment variables to shell or .env file:
 
```dotenv
XKCD_VK_APP_ID= your VK application id
XKCD_VK_GROUP_ID= your VK group id
USER_ACCESS_TOKEN_VK_DVMN= your VK access token
```

By default comics are published by user profile, if you want to publish by group set this option
```dotenv
XKCD_VK_WALL_POST_FROM_GROUP=1
```

To publish:

```bash
foo@bar: dvmn_xkcd] python3 main.py
```


## License

MIT License

Copyright (c) 2019 Roman Kazakov

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.