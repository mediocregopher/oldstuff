#!/usr/bin/perl
# MediocreGopher #

use Socket;
use threads;

local $| = 1;

#Set listening port, create socket
my $port = 80;
socket(SERVER, PF_INET, SOCK_STREAM, getprotobyname('tcp')) or die "socket: $!";
setsockopt(SERVER, SOL_SOCKET, SO_REUSEADDR, 1) or die "setsock: $!";

#Bind socket to port, set it to listen
my $paddr = sockaddr_in($port, INADDR_ANY);
bind(SERVER, $paddr) or die "bind: $!";
listen(SERVER, SOMAXCONN) or die "listen: $!";
print "GOPHER started on port $port \n";

#Tell server to accept connections from clients
while (my $client_addr = accept(MEDIOCRE, SERVER)) {
        my $thread = threads->create(\&mainThread,MEDIOCRE);
        $thread->detach();
}

sub mainThread {

	(my $mediocre) = @_;

	#Set $mediocre pipe to autoflush
	select((select($mediocre), $|=1)[0]);

	#Get destination host and port
	my $dst = receive_post();
	my $address_type = unpack('c',$dst);
	my $dst_dst;
	my $dst_port;
	my $dst_len;
	if ($address_type == 1) {
		$dst_dst = join '.', unpack "xC4", $dst;
		$dst_port = unpack("x5n2",$dst);
	}
	elsif ($address_type == 3) {
		$dst_len = unpack("xC",$dst);
		$dst_dst = unpack("x2A".$dst_len,$dst);
		$dst_port = unpack("x2x".$dst_len."n2",$dst);
	}
	print "$dst_dst:$dst_port\n";
	
	#Set up socket to DST
	my $proto = getprotobyname('tcp');
	my $iaddr = inet_aton($dst_dst);
	my $paddr = sockaddr_in($dst_port, $iaddr);

	#Create $target socket and turn on auto-flush, or die
	my $target;
	socket($target, PF_INET, SOCK_STREAM, $proto) or hindenburg("dst socket: $!");
	connect($target, $paddr) or hindenburg("dst connect: $!");
	select((select($target), $|=1)[0]);

	#Send OK to $mediocre
	send_response('OK');

	#The following loop goes as long as both $mediocre and $target are open.
	#It looks at both handles for new information, then sends that info
	#to its respective destination. Stolen from Michael Auerswald's socks5 script
	while($mediocre || $target) {
		my $rin = "";
		vec($rin, fileno($mediocre), 1) = 1 if $mediocre;
		vec($rin, fileno($target), 1) = 1 if $target;
		my($rout, $eout);
		select($rout = $rin, undef, $eout = $rin, 1);
		if (!$rout  &&  !$eout) { last; }
		my $cbuffer = "";
		my $tbuffer = "";

		if ($mediocre && (vec($eout, fileno($mediocre), 1) || vec($rout, fileno($mediocre), 1))) {
			$tbuffer = receive_post();
			my $result = length($tbuffer);
			if (!defined($result) || !$result) { last; }
		}

		if ($target  &&  (vec($eout, fileno($target), 1)  || vec($rout, fileno($target), 1))) {
			my $result = sysread($target, $cbuffer, 1024000);
			if (!defined($result) || !$result) { last; }
		}

		while (my $len = length($tbuffer)) {
			my $res = syswrite($target, $tbuffer, $len);
			if ($res > 0) { $tbuffer = substr($tbuffer, $res); } else { last; }
		}

		if (length($cbuffer)) {
			send_response($cbuffer);
		}
	}
	
	#Closes connection when everything is done
	shutdown($mediocre,2) or hindenburg("mediocre close: $!");
	shutdown($target,2) or hindenburg("dst close: $!");

	sub receive_post {
		my $content_length;
		my $buffer;
		my $line;

		while ($line ne "\r\n") {
			$line = '';
			while (sysread($mediocre,$buffer,1)) {
				$line .= $buffer;	
				last if $buffer eq "\n";
			}
			if (substr($line,0,16) eq 'Content-Length: ') {
				$content_length = substr($line,16,-2);
			}
		}
		sysread($mediocre,$buffer,$content_length);
		return $buffer;
	}
	
	sub send_response {
		(my $to_send) = @_;
		my $packet;
		$packet .= "HTTP/1.1 200 OK\r\n";
		$packet .= "Server: Apache/2.2.14 (Ubuntu)\r\n";
		$packet .= "X-Powered-By: PHP/5.3.2\r\n";
		$packet .= "Content-Type: text/html; charset=UTF-8\r\n";
		$packet .= "Content-Length: ".length($to_send)."\r\n";
		$packet .= "\r\n$to_send";
		print $mediocre $packet;
	}
	
	sub hindenburg {
		send_response($_[0]);
		die $_[0];
	}
	
}
