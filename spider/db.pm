#!/usr/bin/perl
# DUSTFINGER #

use DBI;

my $dbh;
sub connectToDB() {
	# database information
	my $db="spider";
	my $host="localhost";
	my $userid="apache_nopriv";
	my $passwd='4pach3~r0ck$';
	my $connectionInfo="dbi:mysql:$db:$host";

	# make connection to database
	$dbh = DBI->connect($connectionInfo,$userid,$passwd);
}

sub getConnection {
	return $dbh;
}

connectToDB();
