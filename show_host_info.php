<!DOCTYPE html>
<html>
<body>
<p><?php
    echo "Request served by: ".gethostname()."<br /><br />";
    
    echo "<h2>Request headers</h2>";
    $headers = getallheaders();
    foreach ($headers as $header => $value) {
      echo "$header: $value <br />\n";
    }
    
    echo "<h2>_SERVER data</h2>";
    $headers = $_SERVER;
    foreach ($headers as $header => $value) {
      echo "$header: $value <br />\n";
    }
  ?></p>
</body>