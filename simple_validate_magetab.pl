#!/usr/bin/env perl
#
# This script parsed MAGE-TAB for a given experiment idf
#
# It requires the conda perl-atlas-modules package to be installed

use strict;
use warnings;
use File::Path;
use 5.10.0;

use Bio::MAGETAB::Util::Reader;
use Bio::MAGETAB::Util::Writer::GraphViz;
require Bio::MAGETAB::Util::Writer;


my $reader = Bio::MAGETAB::Util::Reader->new({
   idf            => $ARGV[0],
   relaxed_parser => 0,
});

# Parse the IDF and any associated SDRFs
warn("Parsing MAGE-TAB document...\n");
my ( $inv, $magetab ) = $reader->parse();

# Attempt to use GraphViz to draw the experimental design graph.
warn("Attempting to generate a graph visualisation...\n");
open ( my $fh, '>', 'graph_file_sdrf.png' )
  or die("Error: Unable to open output file: $!");
  my $writer = Bio::MAGETAB::Util::Writer::GraphViz->new({
        sdrfs => [ $inv->get_sdrfs() ],
  });
  my $g = $writer->draw();
  print $fh $g->as_png();

warn("Attempting to write out a new set of MAGE-TAB documents...\n");

mkpath( 'new_path' );
chdir( 'new_path' );

my $writer = Bio::MAGETAB::Util::Writer->new({
  magetab => $magetab,
});

$writer->write();

warn("Done.\n");

