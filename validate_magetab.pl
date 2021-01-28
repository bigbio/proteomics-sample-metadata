#!/usr/bin/env perl
#
# This script parsed MAGE-TAB for a given experiment idf
#
# It requires the conda perl-atlas-modules package to be installed

use strict;
use warnings;
use 5.10.0;

use Bio::MAGETAB::Util::Reader;
my $reader = Bio::MAGETAB::Util::Reader->new({
   idf            => $ARGV[0],
   relaxed_parser => 0,
});
 
my $magetab = $reader->parse();
