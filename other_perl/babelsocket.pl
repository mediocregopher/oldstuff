#!/usr/bin/perl
# MediocreGopher #

use Socket
local $| = 1;

$ARGV[0] =~ /([0-9a-z\.]+):([0-9]+)/i;
my $ip = $1;
my $port = $2;

my $proto = getprotobyname('tcp');
my $iaddr = inet_aton($ip);
my $paddr = sockaddr_in($port, $iaddr);

#Connect to server
socket(SERVER, PF_INET, SOCK_STREAM, $proto) or die "socket: $!";
connect(SERVER, $paddr) or die "connect: $!";

select((select(SERVER), $|=1)[0]);

my $input = <STDIN>;

while ((my $line = <SERVER>) || (my $input = <STDIN>)) {
    if ($input) {
        chomp($input);
        print SERVER $input;
    }
    else {
        print $line;
    }
}


