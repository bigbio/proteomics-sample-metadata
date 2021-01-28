#!/usr/bin/env perl

use strict;
use warnings;

# The following oracle-specific environment variables need to be set here at runtime
# or else all oracle DB connections (e.g. to Conan DB) needed in checks will fail.

BEGIN
{
	$ENV{ORACLE_HOME} = "/sw/arch/dbtools/oracle/product/9.2.0";
	$ENV{ORA_NLS33}   = "/sw/arch/dbtools/oracle/product/9.2.0/ocommon/nls/admin/data";
}

=pod

=head1 NAME

validate_magetab.pl - a script to check that a MAGETAB experiment or array design
is suitable for loading into ArrayExpress

=head1 SYNOPSIS

=over 2

=item B<Experiment mode:>

   validate_magetab.pl -i <IDF file>

   validate_magetab.pl -m <Merged IDF and SDRF file>

   validate_magetab.pl -m <Merged IDF and SDRF file>


=item B<ADF mode:>

   validate_magetab.pl -a <ADF file>

=back

=head1 DESCRIPTION

Script performs basic content validation on the supplied MAGE-TAB file. Note that this script will only attempt to
resolve references within the given file/files. Any reference which has a Term Source REF value of 'ArrayExpress'
is assumed to be available in ArrayExpress and the loader will check this at a later stage.

The script will return 0 if the file is considered safe to load.

Additional curation checks can be run using the -c option. In this case the following logs will be created:

expt_filename_error.log   - All errors and warnings
expt_filename_report.log  - Experiment description information and file list
expt_filename_data.log    - Tabular report describing data files
expt_filename_feature.log - Missing design elements found in data files
expt_ATLAS_filename_error.log - Atlas specific errors and warnings

filename.png - A graph showing links between nodes (materials, assays, data) in the magetab file

=head1 OPTIONS

=over 4

=item B<-i> C<IDF filename>

The MAGE-TAB IDF file to be checked (SDRF file name will be obtained from the IDF)

=item B<-m> C<Merged MAGE-TAB IDF and SDRF filename>

A MAGE-TAB document in which a single IDF and SDRF have been combined (in that order),
with the start of each section marked by [IDF] and [SDRF] respectively. Note that such
documents are not compliant with the MAGE-TAB format specification; this format is used
by ArrayExpress to simplify data submissions.

=item B<-d> C<data directory>

Directory where the data files and SDRF can be found if they are not in the same directory
as the IDF

=item B<-c>

Flag to switch on full curator checking mode, including Atlas checks

=item B<-x>

Flag to indicate that all data file checks should be skipped

=item B<-a> C<ADF filename>

The MAGE-TAB ADF file to be checked.

=item B<-v>

Swtich on verbose logging.

=item B<-h>

Prints a short help text.

=back

=head1 TESTS


=head1 AUTHOR

Anna Farne (farne@ebi.ac.uk), ArrayExpress team, EBI, 2012.

Modified by Emma Hastings (emma@ebi.ac.uk) and Amy Tang (amytang@ebi.ac.uk),
ArrayExpress team, EBI, 2014

Many of the experiment checks were implemented by Tim Rayner.

Acknowledgements go to the ArrayExpress curation team for feature
requests, bug reports and other valuable comments.

=cut

use Pod::Usage;
use Getopt::Long qw(:config no_ignore_case);
use File::Spec;
use Data::Dumper;

use EBI::FGPT::Reader::MAGETAB;
use EBI::FGPT::Writer::Report;

use EBI::FGPT::Reader::ADFParser;

use Log::Log4perl::Appender;
use Log::Log4perl::Level;

# Needed for ADF header recognition before using CPAN parser
# use ArrayExpress::Curator::Config qw($CONFIG);

my $svn_revision = '$Revision$';
our ($VERSION) = ( $svn_revision =~ /^\$Revision: ([\d\.]*)/ );

sub parse_args
{

	my ( %args, $want_help );
	GetOptions(
				"m|merged=s"   => \$args{merged_filename},
				"i|idf=s"      => \$args{idf_filename},
				"h|help"       => \$want_help,
				"v|verbose"    => \$args{verbose},
				"d|data_dir=s" => \$args{data_dir},
				"c|curate"     => \$args{curate},
				"x|skip_data"  => \$args{skip_data},
				"a|adf=s"      => \$args{adf_filename},
				"l|log=s"      => \$args{adf_logdir},
	);


	if ($want_help)
	{
		pod2usage(
				   -exitval => 255,
				   -output  => \*STDOUT,
				   -verbose => 1,
		);
	}

	unless ( $args{merged_filename} || $args{idf_filename} || $args{adf_filename} )
	{
		pod2usage(
				   -message => 'You must provide an ADF, IDF or merged IDF/SDRF file.',
				   -exitval => 255,
				   -output  => \*STDOUT,
				   -verbose => 0,
		);
	}

	if ( $args{idf_filename} and $args{merged_filename} )
	{
		pod2usage(
				   -message => 'You cannot provide an IDF AND merged IDF/SDRF file.',
				   -exitval => 255,
				   -output  => \*STDOUT,
				   -verbose => 0,
		);
	}

	if ( $args{adf_filename} and ( $args{merged_filename} || $args{idf_filename} ) )
	{
		pod2usage(
			-message => 'You cannot provide an ADF AND an IDF or merged magetab document',
			-exitval => 255,
			-output  => \*STDOUT,
			-verbose => 0,
		);
	}
	return ( \%args );
}

# Get our arguments
my $args = parse_args();

### ADF CHECKS ###

# Did not specify any log file locations as the ADF loader should be capturing
# the STDOUT messages (INFO, WARN and ERROR alike)

if ( $args->{adf_filename} ) {

    my $adf_checker = EBI::FGPT::Reader::ADFParser->new({
         'adf_path'   => $args->{adf_filename},
         'verbose_logging' => $args->{verbose}
    });

    $adf_checker->check;

    # Check for the presence of a single, valid accession number:

    my $arraydesign = $adf_checker->get_arraydesign;

    my @accession_number =  grep {$_->get_name =~/ArrayExpressAccession/} @{ $arraydesign->get_comments || []};

    if (scalar @accession_number == 0) {
       $adf_checker->error("Comment[ArrayExpressAccession] is missing. ADF is not valid for database loading.");
    } elsif (scalar @accession_number > 1) {
        $adf_checker->error("There are multiple accession numbers in Comment[ArrayExpressAccession].");
    } elsif ($accession_number[0]->get_value !~/A-[A-Z]{4}-\d+/) {
        $adf_checker->error("The accession ".$accession_number[0]->get_value." is not in ArrayExpress format.");
    }

    my $checker_status_appender = Log::Log4perl->appender_by_name("adf_checker_status")
              or die("Could not find log appender named '\adf_checker_status\'.");

    print "\n";
    print "Number of ADF warnings: "
          . $checker_status_appender->howmany("WARN") . "\n";
    print "Number of ADF errors: "
          . $checker_status_appender->howmany("ERROR") . "\n";


    if ($adf_checker->has_errors) {
       exit 1;
    } else {
       exit 0;
    }
}

### EXPERIMENT CHECKS ###

# Checker will always perform basic validation checks
# Can specify that it runs additional checks as required
my $check_sets;

my $reader_params;

# Some curation specific reporting set up
if ( $args->{curate} )
{

	# Checks sets have no name because we do not want to
	# create log files for them in curation mode
#	$check_sets->{'EBI::FGPT::CheckSet::AEArchive'} = '';
#	$check_sets->{'EBI::FGPT::CheckSet::Curation'}  = '';
	$check_sets->{'EBI::FGPT::CheckSet::AEAtlas'}   = '';

	my $reporter = Log::Log4perl::Appender->new(
												 "EBI::FGPT::Writer::Report",
												 name       => "report_writer",
												 additivity => 1,
	);

	$reporter->threshold($INFO);
	$reader_params->{report_writer} = $reporter;

	#Create Atlas log
	my $atlas_reporter = Log::Log4perl::Appender->new(
													   "EBI::FGPT::Writer::Report",
													   name => "atlas_report_writer",
													   additivity => 1,
	);

	$atlas_reporter->threshold($INFO);
	$reader_params->{atlas_report_writer} = $atlas_reporter;

	# When running in curation mode we want to add a temporary
	# AE accession so that validation does not fail due to missing accession
	$reader_params->{accession} = "DUMMY";

} else
{

	# ae_validation log file will be created
	$check_sets->{'EBI::FGPT::CheckSet::AEArchive'} = 'ae_validation';
}

# Set up parser params depending on script args provided
$reader_params->{'check_sets'}       = $check_sets;
$reader_params->{'skip_data_checks'} = $args->{'skip_data'};

my $filename;

if ( $args->{idf_filename} )
{
	$reader_params->{idf} = $args->{idf_filename};
	$filename = $args->{idf_filename};
} else
{
	$reader_params->{mtab_doc} = $args->{merged_filename};
	$filename = $args->{merged_filename};
}

if ( $args->{data_dir} )
{
	$reader_params->{data_dir} = $args->{data_dir};
} else
{
	my ( $vol, $dir, $file ) = File::Spec->splitpath($filename);
	$dir ||= ".";
	$reader_params->{data_dir} = $dir;
}

if( $args->{ "verbose" } ) {
    $reader_params->{ "verbose_logging" } = 1;
}

print "\nData dir: " . $reader_params->{data_dir} . "\n\n";

my $checker = EBI::FGPT::Reader::MAGETAB->new($reader_params);

$checker->parse();

$checker->print_checker_status();

END
{

	# Attempt to delete Config.yml which is created by PAR unpacking process
	# We will remove the requirement to have this file in the PAR archive
	# during refactoring (it is needed by ArrayExpress::Curator::Config)
	if ( -r "Config.yml" )
	{
		my $mtime = -M "Config.yml";

		# If file was created after script started we delete it
		# We do this check to avoid deleting Config files which are
		# not related to the running of this script
		if ( $mtime < 0 )
		{
			unlink "Config.yml";
		}
	}
}

if ( $checker->has_errors )
{
	exit 1;
} else
{
	exit 0;
}
