mkdir output
shodan search --limit 10 --fields ip_str,port 'product:"Cobalt Strike Beacon"' > output/cobaltstrike.txt
shodan search --limit 10 --fields ip_str,port 'ssl:MetasploitSelfSignedCA' > output/metasploit.txt
shodan search --limit 10 --fields ip_str,port 'ssl:multiplayer ssl:operators' > output/sliverc2.txt
