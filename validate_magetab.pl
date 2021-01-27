#!/usr/bin/env perl
#
# This script parsed MAGE-TAB for a given experiment idf
#
# It requires the conda perl-atlas-modules package to be installed

use strict;
use warnings;
use 5.10.0;

# MAGE-TAB parsing.
use Atlas::Magetab4Atlas;

my $magetab4atlas = Atlas::Magetab4Atlas->new( "idf_filename" => $ARGV[0] );

print "Accession:".$magetab4atlas;

foreach my $assay4atlas (@{ $magetab4atlas->get_assays }) {
  # Get assay name
  print "Assay:".$assay4atlas->get_name;
}
