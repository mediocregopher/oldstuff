#!/usr/bin/perl
# MediocreGopher #

use Socket;
use threads;

local $| = 1;

$ARGV[0] ? my $gopher_loc = $ARGV[0] : die "First parameter needs to be ip address or host name of gopher server";

#Set port, create socket
my $port = $ARGV[1] ? $ARGV[1] : 6666;
socket(SERVER, PF_INET, SOCK_STREAM, getprotobyname('tcp')) or die "socket: $!";
setsockopt(SERVER, SOL_SOCKET, SO_REUSEADDR, 1) or die "setsock: $!";

#Bind socket to port, set it to listen
my $paddr = sockaddr_in($port, INADDR_ANY);
bind(SERVER, $paddr) or die "bind: $!";
listen(SERVER, SOMAXCONN) or die "listen: $!";
print "MEDIOCRE started on port $port \n";

#Tell server to accept connections
while (my $client_addr = accept(CLIENT, SERVER)) {
        my $thread = threads->create(\&mainThread,CLIENT);
        $thread->detach();
}

sub mainThread { 
	(my $client) = @_;

	#Set $client pipe to autoflush
	select((select($client), $|=1)[0]);

	#Scope data variable and remove first 0x05 from client->server stream
	my $data;
	socks5_byte();

	#C->S:  Get # of supported protocols, then process them. if No-Authentication is not supported
	#	displays error and kills server
	my $num_prots_supported = ord(data(1));
	for (my $i=0;$i<$num_prots_supported;$i++) {
		if (ord(data(1)) == 0) {data($num_prots_supported-($i+1));last;}
		elsif ($i == $num_prots_supported - 1) {
			print $client pack('H*','05FF');
			die "No-Authentication not supported\n";
		}
	}

	#S->C:  Tell client to use No-Authentication
	print $client pack('H*','0500');

	#C->S:  Remove first 0x05, get command code, make sure it's to establish tcp/ip stream
	socks5_byte();
	my $command_code_raw = data(1);
	my $command_code = ord($command_code_raw);
	unless(unpack('H*',$command_code_raw)) {
		print $client pack('H*','0507');
		die "mediocre: client connection terminated";
	}
	if ($command_code != 1) {
		print $client pack('H*','0507');
		die "mediocre: this proxy software only supports tcp/ip streams";
	}
	data(1); #empty byte

	#C-S:  Gets either IPv4 address or hostname
	my $address_type = ord(data(1));
	my ($dst_dst_h,$dst_dst,$dst_dst_length_h,$dst_port_h);
	if ($address_type == 1) {
		$dst_dst_h = data(4);
		$dst_dst = join('.', unpack("C*",$dst_dst_h));
		$dst_port_h = data(2);		
	}
	elsif ($address_type == 3) {
		$dst_dst_length_h = data(1);
		$dst_dst_h = data(ord($dst_dst_length_h));
		$dst_dst = unpack("A*",$dst_dst_h);
		$dst_port_h = data(2);
	}
	else {
		print $client pack('H*','0508');
		die "mediocre: this proxy software only supports IPv4 and domain names";
	}

	#Set up socket to $gopher
	my $proto = getprotobyname('tcp');
	my $iaddr = inet_aton($gopher_loc);
	my $paddr = sockaddr_in(80, $iaddr);

	print $dst_dst."\n";

	#Create $gopher socket and turn on auto-flush, or die
	socket(my $gopher, PF_INET, SOCK_STREAM, $proto) or die "gopher socket: $!";
	connect($gopher, $paddr) or die "gopher connect: $!";
	select((select($gopher), $|=1)[0]);

	#Tell $gopher what to connect to
	send_post(pack('H*','0'.$address_type).$dst_dst_length_h.$dst_dst_h.$dst_port_h);

	#See if it did so, error otherwise
	my $response = receive_response();
	if ($response ne 'OK') {
		print $client pack('H*','0501');
		die $response;
	}

	#S->C:  Inform client that connection has been successfully made to destination
	#	(or die)
	print $client pack('H*',"0500000".$address_type).$dst_dst_length_h.$dst_dst_h.$dst_port_h;
	die "$response" if $return_code != 0;

	#The following loop goes as long as both $client and $gopher are open.
	#It looks at both handles for new information, then sends that info
	#to its respective destination. Stolen from Michael Auerswald's socks5 script
	##########################################################################
	#I have no idea how this works!!
	while($client || $gopher) {
		my $rin = "";
		vec($rin, fileno($client), 1) = 1 if $client;
		vec($rin, fileno($gopher), 1) = 1 if $target;
		my($rout, $eout);
		select($rout = $rin, undef, $eout = $rin, 1);
		if (!$rout  &&  !$eout) { last; }
		my $cbuffer = "";
		my $tbuffer = "";

		if ($client && (vec($eout, fileno($client), 1) || vec($rout, fileno($client), 1))) {
			my $result = sysread($client, $tbuffer, 1024);
			#print "tbuffer:\n".$tbuffer."\n";
			if (!defined($result) || !$result) { last; }
		}

		if ($gopher  &&  (vec($eout, fileno($target), 1)  || vec($rout, fileno($target), 1))) {
			$cbuffer = receive_response();
			my $result = length($cbuffer);
			#print "cbuffer:\n".$cbuffer."\n";
			if (!defined($result) || !$result) { last; }
		}

		if (length($tbuffer)) {
			send_post($tbuffer);
		}

		while (my $len = length($cbuffer)) {
			my $res = syswrite($client, $cbuffer, $len);
			if ($res > 0) { $cbuffer = substr($cbuffer, $res); } else { last; }
		}
	}
	
	#Closes connection when everything is done
	shutdown($client,2) or die "client close: $!";
	shutdown($gopher,2) or die "gopher close: $!";

	#Shortcut for using sysread with $client. Returns the data as well, which is useful
	sub data {
		sysread($client,$data,$_[0]);
		return $data;
	}

	#Makes sure the client is using socks5 for each message sent
	sub socks5_byte {
		die "Client not using socks5\n" if (data(1) != "\x05");
	}

	sub send_post {
		(my $to_send) = @_;
		my $packet;
		$packet .= "POST /gopher HTTP/1.1\r\n";
		$packet .= "User-Agent: Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)\r\n";
		$packet .= "Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7\r\n";
		$packet .= "Keep-Alive: 300\r\n";
		$packet .= "Connection: keep-alive\r\n";
		$packet .= "Content-Type: application/octet-stream\r\n";
		$packet .= "Content-Length: ".length($to_send)."\r\n";
		$packet .= "\r\n$to_send";
		print $gopher $packet;
	}

	sub receive_response {
		my $content_length;
		my $buffer;
		my $line;

		while ($line ne "\r\n") {
			$line = '';
			while (sysread($gopher,$buffer,1)) {
				$line .= $buffer;	
				last if $buffer eq "\n";
			}
			if (substr($line,0,16) eq 'Content-Length: ') {
				$content_length = substr($line,16,-2);
			}
		}
		sysread($gopher,$buffer,$content_length);
		return $buffer;
	}
}
