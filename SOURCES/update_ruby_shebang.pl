#!/usr/bin/perl

use warnings;
use strict;

my @files = split (/\n/, `find . -type f -print | xargs grep -l '/usr/bin/ruby'`);

foreach my $file (@files) {
    print "Inspecting file for ruby shebang: $file\n";

    my $found = 0;

    if (open my $fh, "<", $file) {
        my $line = <$fh>;

        $found = 1 if ($line =~ m:^#!.*/usr/bin/ruby:);
        $found = 1 if ($line =~ m:^#!/usr/bin/env ruby:);

        if ($found) {
            print $line;
        }

        close $fh;
    }

    if ($found) {
        print "Editting: $file\n";
        print `sed -i '1s:^#!.*ruby.*\$:#!/opt/cpanel/ea-ruby27/root/usr/bin/ruby:' $file` . "\n";
    }
}

