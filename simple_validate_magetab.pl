#!/usr/bin/env perl
#
# This script parsed MAGE-TAB for a given experiment idf
#
# It requires the conda perl-atlas-modules package to be installed.
# Description:
#     The script takes one parameter project accession if the idf wants to be generated for only one accession.

use strict;
use warnings;
use File::Path;
use 5.10.0;

use Bio::MAGETAB::Util::Reader;
use Bio::MAGETAB::Util::Writer::GraphViz;
require Bio::MAGETAB::Util::Writer;
use File::Find::Rule;
use Try::Tiny;

use Bio::MAGETAB::Util::Writer::IDF;
use Bio::MAGETAB::Util::Writer::ADF;
use Bio::MAGETAB::Util::Writer::SDRF;

use File::Basename;

my $project = '';
if (@ARGV){
  $project = $ARGV[0];
}


my $includeFiles = File::Find::Rule->file()->name('*.idf.tsv'); # search by file extensions
if ($project ne ''){
   $includeFiles = File::Find::Rule->file()
     ->name($project . '*idf.tsv'); # search by file extensions

}
my $count_errors = 0;
my $count_projects = 0;
my @files = File::Find::Rule->or($includeFiles)->in('annotated-projects/');



foreach (@files){

  print('Validating project ' . $_ . "\n");
  $count_projects = $count_projects + 1;

  try{
    my $reader = Bio::MAGETAB::Util::Reader->new({
      idf            => $_,
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
    print "Writing the new MAGE-TAB: " . $_ . "\n";

    mkpath( 'new_path' );
    open( my $filehandler, ">", "new_path/file_idf.idf.tsv" )
      or die("Error: Unable to open output file: $!");

    $writer = Bio::MAGETAB::Util::Writer->new({
      magetab => $magetab,
      filehandle => $filehandler,
    });

    $writer->write();
    warn("Done.\n");

  }catch {
    warn "caught error: $_"; # not $@
    $count_errors = $count_errors + 1;
  };
}

if($count_errors != 0){
  print ("Number of projects validated: " . $count_projects . " , projects with errors " . $count_errors . "\n");
  exit -1;
}

print ("Number of projects validated: " . $count_projects . " , no errors\n");





