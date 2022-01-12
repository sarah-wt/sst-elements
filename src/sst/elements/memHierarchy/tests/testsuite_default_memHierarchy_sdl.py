# -*- coding: utf-8 -*-

from sst_unittest import *
from sst_unittest_support import *
import os.path

################################################################################
# Code to support a single instance module initialize, must be called setUp method

module_init = 0
module_sema = threading.Semaphore()

def initializeTestModule_SingleInstance(class_inst):
    global module_init
    global module_sema

    module_sema.acquire()
    if module_init != 1:
        try:
            # Put your single instance Init Code Here
            pass
        except:
            pass
        module_init = 1
    module_sema.release()

################################################################################
################################################################################
################################################################################

class testcase_memHierarchy_sdl(SSTTestCase):

    def initializeClass(self, testName):
        super(type(self), self).initializeClass(testName)
        # Put test based setup code here. it is called before testing starts
        # NOTE: This method is called once for every test

    def setUp(self):
        super(type(self), self).setUp()
        initializeTestModule_SingleInstance(self)
        # Put test based setup code here. it is called once before every test

    def tearDown(self):
        # Put test based teardown code here. it is called once after every test
        super(type(self), self).tearDown()

#####

    def test_memHierarchy_sdl_1(self):
        #  sdl-1   Simple CPU + 1 level cache + Memory
        self.memHierarchy_Template("sdl-1")

    def test_memHierarchy_sdl_2(self):
        #  sdl-2  Simple CPU + 1 level cache + DRAMSim Memory
        self.memHierarchy_Template("sdl-2")

    def test_memHierarchy_sdl_3(self):
        #  sdl-3  Simple CPU + 1 level cache + DRAMSim Memory (alternate block size)
        self.memHierarchy_Template("sdl-3")

    def test_memHierarchy_sdl2_1(self):
        #  sdl2-1  Simple CPU + 2 levels cache + Memory
        self.memHierarchy_Template("sdl2-1")

    def test_memHierarchy_sdl3_1(self):
        #  sdl3-1  2 Simple CPUs + 2 levels cache + Memory
        self.memHierarchy_Template("sdl3-1")

    def test_memHierarchy_sdl3_2(self):
        #  sdl3-2  2 Simple CPUs + 2 levels cache + DRAMSim Memory
        self.memHierarchy_Template("sdl3-2")

    def test_memHierarchy_sdl3_3(self):
        self.memHierarchy_Template("sdl3-3")

    def test_memHierarchy_sdl4_1(self):
        self.memHierarchy_Template("sdl4-1")

    @skip_on_sstsimulator_conf_empty_str("DRAMSIM", "LIBDIR", "DRAMSIM is not included as part of this build")
    def test_memHierarchy_sdl4_2_dramsim(self):
        self.memHierarchy_Template("sdl4-2", ignore_err_file=True)

    @skip_on_sstsimulator_conf_empty_str("RAMULATOR", "LIBDIR", "RAMULATOR is not included as part of this build")
    def test_memHierarchy_sdl4_2_ramulator(self):
        self.memHierarchy_Template("sdl4-2-ramulator")

    @skip_on_sstsimulator_conf_empty_str("DRAMSIM", "LIBDIR", "DRAMSIM is not included as part of this build")
    def test_memHierarchy_sdl5_1_dramsim(self):
        self.memHierarchy_Template("sdl5-1", ignore_err_file=True)

    @skip_on_sstsimulator_conf_empty_str("RAMULATOR", "LIBDIR", "RAMULATOR is not included as part of this build")
    def test_memHierarchy_sdl5_1_ramulator(self):
        if testing_check_get_num_ranks() > 1 or testing_check_get_num_threads() > 1:
            self.memHierarchy_Template("sdl5-1-ramulator_MC")
        else:
            self.memHierarchy_Template("sdl5-1-ramulator")

    def test_memHierarchy_sdl8_1(self):
        self.memHierarchy_Template("sdl8-1")

    def test_memHierarchy_sdl8_3(self):
        self.memHierarchy_Template("sdl8-3")

    def test_memHierarchy_sdl8_4(self):
        self.memHierarchy_Template("sdl8-4")

    def test_memHierarchy_sdl9_1(self):
        self.memHierarchy_Template("sdl9-1")

    def test_memHierarchy_sdl9_2(self):
        self.memHierarchy_Template("sdl9-2")

#####

    def memHierarchy_Template(self, testcase, ignore_err_file=False):
        # Get the path to the test files
        test_path = self.get_testsuite_dir()
        outdir = self.get_test_output_run_dir()
        tmpdir = self.get_test_output_tmp_dir()

        # Some tweeking of file names are due to inconsistencys with testcase name
        testcasename_sdl = testcase.replace("_MC", "")
        testcasename_out = testcase.replace("-", "_")

        # Set the various file paths
        testDataFileName=("test_memHierarchy_{0}".format(testcasename_out))
        sdlfile = "{0}/{1}.py".format(test_path, testcasename_sdl)
        reffile = "{0}/refFiles/{1}.out".format(test_path, testDataFileName)
        outfile = "{0}/{1}.out".format(outdir, testDataFileName)
        errfile = "{0}/{1}.err".format(outdir, testDataFileName)
        mpioutfiles = "{0}/{1}.testfile".format(outdir, testDataFileName)

        log_debug("testcase = {0}".format(testcase))
        log_debug("sdl file = {0}".format(sdlfile))
        log_debug("ref file = {0}".format(reffile))

        # Run SST in the tests directory
        self.run_sst(sdlfile, outfile, errfile, set_cwd=test_path, mpi_out_files=mpioutfiles)

        # Lines to ignore
        # These are generated by DRAMSim
        ignore_lines = ["===== MemorySystem"]
        ignore_lines.append("TOTAL_STORAGE : 2048MB | 1 Ranks | 16 Devices per rank") 
        ignore_lines.append("== Loading")
        ignore_lines.append("DRAMSim2 Clock Frequency =1Hz, CPU Clock Frequency=1Hz")
        ignore_lines.append("WARNING: UNKNOWN KEY 'DEBUG_TRANS_FLOW' IN INI FILE")
        # This is generated by SST when the number of ranks/threads > # of components
        ignore_lines.append("WARNING: No components are assigned to")
        #These are warnings/info generated by SST/memH in debug mode
        ignore_lines.append("Notice: memory controller's region is larger than the backend's mem_size")
        ignore_lines.append("Region: start=")
        # This may be present if ranks < 2
        ignore_lines.append("not aligned to the request size")

        # Statistics that count occupancy on each cycle sometimes diff in parallel execution
        # due to the synchronization interval sometimes allowing the clock to run ahead a cycle or so
        tol_stats = { "outstanding_requests" : [0, 0, 20, 0, 0], # Only diffs in number of cycles
                      "total_cycles" : [20, 'X', 20, 20, 20],    # This stat is set once at the end of sim. May vary in all fields
                      "MSHR_occupancy" : [0, 0, 20, 0, 0] }      # Only diffs in number of cycles

        filesAreTheSame, statDiffs, othDiffs = testing_stat_output_diff(outfile, reffile, ignore_lines, tol_stats, True)
        
        # Perform the tests
        if ignore_err_file is False:
            if os_test_file(errfile, "-s"):
                log_testing_note("memHierarchy SDL test {0} has a Non-Empty Error File {1}".format(testDataFileName, errfile))

        if filesAreTheSame:
            log_debug(" -- Output file {0} passed check against the Reference File {1}".format(outfile, reffile))
        else:
            diffdata = self._prettyPrintDiffs(statDiffs, othDiffs)
            log_failure(diffdata)
            self.assertTrue(filesAreTheSame, "Output file {0} does not pass check against the Reference File {1} ".format(outfile, reffile))

###

    # Remove lines containing any string found in 'remove_strs' from in_file
    # If out_file != None, output is out_file
    # Otherwise, in_file is overwritten
    def _remove_lines_cleanup_file(self, remove_strs, in_file, out_file = None, append = False):
        with open(in_file, 'r') as fp:
            lines = fp.readlines()
        
        if out_file == None:
            out_file = in_file

        if append == True:
            mode = 'a'
        else:
            mode = 'w'
        
        with open(out_file, mode) as fp:
            if not append:
                fp.truncate(0)
            for line in lines:
                skip = False
                for search in remove_strs:
                    if search in line:
                        skip = True
                        continue
                if not skip:
                    fp.write(line)

    def _prettyPrintDiffs(self, stat_diff, oth_diff):
        out = ""
        if len(stat_diff) != 0:
            out = "Statistic diffs:\n"
            for x in stat_diff:
                out += (x[0] + " " + ",".join(str(y) for y in x[1:]) + "\n")
        
        if len(oth_diff) != 0:
            out += "Non-statistic diffs:\n"
            for x in oth_diff:
                out += x[0] + " " + x[1] + "\n"

        return out
