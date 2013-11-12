
#include <execinfo.h>
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include "pin.H"
#include <time.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <iostream>
#include <fstream>
#include <map>
#include <stack>
#include <ctime>
#include <bitset>

KNOB<string> SSTNamedPipe(KNOB_MODE_WRITEONCE, "pintool",
    "p", "", "Named pipe to connect to SST simulator");
KNOB<UINT64> MaxInstructions(KNOB_MODE_WRITEONCE, "pintool",
    "i", "10000000000", "Maximum number of instructions to run");
KNOB<UINT32> SSTVerbosity(KNOB_MODE_WRITEONCE, "pintool",
    "v", "0", "SST verbosity level");
KNOB<UINT32> MaxCoreCount(KNOB_MODE_WRITEONCE, "pintool",
    "c", "1", "Maximum core count to use for data pipes.");
KNOB<UINT32> StartupMode(KNOB_MODE_WRITEONCE, "pintool",
    "s", "1", "Mode for configuring profile behavior, 1 = start enabled, 0 = start disabled");

//PIN_LOCK pipe_lock;
UINT32 core_count;
int* pipe_id;
bool enable_output;

#define PERFORM_EXIT 1
#define PERFORM_READ 2
#define PERFORM_WRITE 4
#define START_DMA 8
#define ISSUE_TLM_MAP 80
#define ISSUE_TLM_FREE 100
#define START_INSTRUCTION 32
#define END_INSTRUCTION 64

VOID Fini(INT32 code, VOID *v)
{
	if(SSTVerbosity.Value() > 0) {
		std::cout << "SSTARIEL: Execution completed, shutting down." << std::endl;
	}

	uint8_t command = PERFORM_EXIT;
	write(pipe_id[0], &command, sizeof(command));

	for(int i = 0; i < core_count; ++i) {
		// Close the pipe and clean up
		close(pipe_id[i]);
	}
}

VOID copy(void* dest, const void* input, UINT32 length) {
	for(UINT32 i = 0; i < length; ++i) {
		((char*) dest)[i] = ((char*) input)[i];
	}
}

VOID WriteInstructionRead(ADDRINT* address, UINT32 readSize, THREADID thr) {
	if(enable_output) {
		const uint8_t read_marker = PERFORM_READ;
		uint64_t addr64 = (uint64_t) address;
		uint32_t thrID = (uint32_t) thr;

		const UINT32 BUFFER_LENGTH = sizeof(read_marker) + sizeof(addr64) + sizeof(readSize);

		char buffer[BUFFER_LENGTH];
		copy(&buffer[0], &read_marker, sizeof(read_marker));
		copy(&buffer[sizeof(read_marker)], &addr64, sizeof(addr64));
		copy(&buffer[sizeof(read_marker) + sizeof(addr64)], &readSize, sizeof(readSize));

		assert(thr < core_count);
		write(pipe_id[thr], buffer, BUFFER_LENGTH);
	}
}

VOID WriteInstructionWrite(ADDRINT* address, UINT32 writeSize, THREADID thr) {
	if(enable_output) {
		const uint8_t writer_marker = PERFORM_WRITE;
		uint64_t addr64 = (uint64_t) address;
		uint32_t thrID = (uint32_t) thr;

		size_t write_size;

		const UINT32 BUFFER_LENGTH = sizeof(writer_marker) + sizeof(addr64) + sizeof(writeSize);
		char buffer[BUFFER_LENGTH];

		copy(&buffer[0], &writer_marker, sizeof(writer_marker));
		copy(&buffer[sizeof(writer_marker)], &addr64, sizeof(addr64));
		copy(&buffer[sizeof(writer_marker) + sizeof(addr64)], &writeSize, sizeof(writeSize));

		write(pipe_id[thrID], buffer, BUFFER_LENGTH);
	}
}

VOID WriteStartInstructionMarker(UINT32 thr) {
	const uint8_t inst_marker = START_INSTRUCTION;
	write(pipe_id[thr], &inst_marker, sizeof(inst_marker));
}

VOID WriteEndInstructionMarker(UINT32 thr) {
	const uint8_t inst_marker = END_INSTRUCTION;
	write(pipe_id[thr], &inst_marker, sizeof(inst_marker));
}

VOID WriteInstructionReadWrite(THREADID thr, ADDRINT* readAddr, UINT32 readSize,
	ADDRINT* writeAddr, UINT32 writeSize) {

	if(enable_output) {
		if(thr < core_count) {
			const uint8_t start_ins     = (uint8_t) START_INSTRUCTION;
		        const uint8_t end_ins       = (uint8_t) END_INSTRUCTION;
			const uint8_t writer_marker = (uint8_t) PERFORM_WRITE;
		        const uint8_t read_marker   = (uint8_t) PERFORM_READ;

			const uint64_t wAddr64 = (uint64_t) writeAddr;
			const uint32_t wSize   = (uint32_t) writeSize;
		        const uint64_t rAddr64 = (uint64_t) readAddr;
		        const uint32_t rSize   = (uint32_t) readSize;

			const uint32_t thrID = (uint32_t) thr;

			const UINT32 BUFFER_LENGTH = (uint32_t) (sizeof(start_ins) + sizeof(end_ins) +
				sizeof(writer_marker) + sizeof(wAddr64) + sizeof(wSize) +
				sizeof(read_marker) + sizeof(rAddr64) + sizeof(rSize));

			char* buffer = (char*) malloc(sizeof(char) * BUFFER_LENGTH);
			int index = 0;

			copy(&buffer[index], &start_ins, sizeof(start_ins));
			index += sizeof(start_ins);
			copy(&buffer[index], &read_marker, sizeof(read_marker));
			index += sizeof(read_marker);
			copy(&buffer[index], &rAddr64, sizeof(rAddr64));
			index += sizeof(rAddr64);
			copy(&buffer[index], &rSize, sizeof(rSize));
			index += sizeof(rSize);
			copy(&buffer[index], &writer_marker, sizeof(writer_marker));
			index += sizeof(writer_marker);
			copy(&buffer[index], &wAddr64, sizeof(wAddr64));
			index += sizeof(wAddr64);
			copy(&buffer[index], &wSize, sizeof(wSize));
			index += sizeof(wSize);
			copy(&buffer[index], &end_ins, sizeof(end_ins));

			assert(thr < core_count);
			write(pipe_id[thrID], buffer, BUFFER_LENGTH);

			free(buffer);
		}
	}

}

VOID WriteInstructionReadOnly(THREADID thr, ADDRINT* readAddr, UINT32 readSize) {

	if(enable_output) {
		if(thr < core_count) {
			const uint8_t start_ins     = (uint8_t) START_INSTRUCTION;
		        const uint8_t end_ins       = (uint8_t) END_INSTRUCTION;
			const uint8_t writer_marker = (uint8_t) PERFORM_WRITE;
		        const uint8_t read_marker   = (uint8_t) PERFORM_READ;

		       	const uint64_t rAddr64 = (uint64_t) readAddr;
		       	const uint32_t rSize   = (uint32_t) readSize;

			const uint32_t thrID = (uint32_t) thr;

		       	const UINT32 BUFFER_LENGTH = (uint32_t) (sizeof(start_ins) + sizeof(end_ins) +
		               	sizeof(read_marker) + sizeof(rAddr64) + sizeof(rSize));

			char* buffer = (char*) malloc(sizeof(char) * BUFFER_LENGTH);
			int index = 0;

		       	copy(&buffer[index], &start_ins, sizeof(start_ins));
			index += sizeof(start_ins);
		       	copy(&buffer[index], &read_marker, sizeof(read_marker));
			index += sizeof(read_marker);
		       	copy(&buffer[index], &rAddr64, sizeof(rAddr64));
			index += sizeof(rAddr64);
		       	copy(&buffer[index], &rSize, sizeof(rSize));
			index += sizeof(rSize);
		        copy(&buffer[index], &end_ins, sizeof(end_ins));

			write(pipe_id[thrID], buffer, BUFFER_LENGTH);
			free(buffer);
		}
	}

}

VOID WriteInstructionWriteOnly(THREADID thr, ADDRINT* writeAddr, UINT32 writeSize) {

	if(enable_output) {
		if(thr < core_count) {
			const uint8_t start_ins     = (uint8_t) START_INSTRUCTION;
		        const uint8_t end_ins       = (uint8_t) END_INSTRUCTION;
			const uint8_t writer_marker = (uint8_t) PERFORM_WRITE;
		        const uint8_t read_marker   = (uint8_t) PERFORM_READ;

		       	const uint64_t wAddr64 = (uint64_t) writeAddr;
		       	const uint32_t wSize   = (uint32_t) writeSize;

			const uint32_t thrID = (uint32_t) thr;

		       	const UINT32 BUFFER_LENGTH = (uint32_t) (sizeof(start_ins) + sizeof(end_ins) +
		               	sizeof(writer_marker) + sizeof(wAddr64) + sizeof(wSize));

			char* buffer = (char*) malloc(sizeof(char) * BUFFER_LENGTH);
			int index = 0;

		       	copy(&buffer[index], &start_ins, sizeof(start_ins));
			index += sizeof(start_ins);
		       	copy(&buffer[index], &writer_marker, sizeof(writer_marker));
			index += sizeof(writer_marker);
		       	copy(&buffer[index], &wAddr64, sizeof(wAddr64));
			index += sizeof(wAddr64);
		        copy(&buffer[index], &wSize, sizeof(wSize));
			index += sizeof(wSize);
		        copy(&buffer[index], &end_ins, sizeof(end_ins));

			assert(thr < core_count);
			write(pipe_id[thrID], buffer, BUFFER_LENGTH);
			free(buffer);
		}
	}

}

VOID InstrumentInstruction(INS ins, VOID *v)
{
	if( INS_IsMemoryRead(ins) && INS_IsMemoryWrite(ins) ) {
		INS_InsertPredicatedCall(ins, IPOINT_BEFORE, (AFUNPTR)
			WriteInstructionReadWrite,
			IARG_THREAD_ID,
			IARG_MEMORYREAD_EA, IARG_UINT32, INS_MemoryReadSize(ins),
			IARG_MEMORYWRITE_EA, IARG_UINT32, INS_MemoryWriteSize(ins),
			IARG_END);
	} else if( INS_IsMemoryRead(ins) ) {
		INS_InsertPredicatedCall(ins, IPOINT_BEFORE, (AFUNPTR)
			WriteInstructionReadOnly,
			IARG_THREAD_ID,
			IARG_MEMORYREAD_EA, IARG_UINT32, INS_MemoryReadSize(ins),
			IARG_END);
	} else if( INS_IsMemoryWrite(ins) ) {
		INS_InsertPredicatedCall(ins, IPOINT_BEFORE, (AFUNPTR)
			WriteInstructionWriteOnly,
			IARG_THREAD_ID,
			IARG_MEMORYWRITE_EA, IARG_UINT32, INS_MemoryWriteSize(ins),
			IARG_END);
	}

}

int ariel_tlvl_memcpy(void* dest, void* source, size_t size) {
#ifdef ARIEL_DEBUG
	printf("Perform a tlvl_memcpy from Ariel from %p to %p length %llu\n",
		source, dest, size);
#endif

	char* dest_c = (char*) dest;
	char* src_c  = (char*) source;

	// Perform the memory copy on behalf of the application
	for(size_t i = 0; i < size; ++i) {
		dest_c[i] = src_c[i];
	}

	THREADID currentThread = PIN_ThreadId();
	UINT32 thr = (UINT32) currentThread;

	if(thr >= core_count) {
		printf("Thread ID: %lu is greater than core count.\n", thr);
		exit(-4);
	}

	const uint8_t issueDMAMarker = (uint8_t) START_DMA;
	const uint64_t ariel_src     = (uint64_t) source;
        const uint64_t ariel_dest    = (uint64_t) dest;
        const uint32_t length        = (uint32_t) size;

        const int BUFFER_LENGTH = sizeof(issueDMAMarker) + sizeof(ariel_src) +
		sizeof(ariel_dest) + sizeof(length);

	char* buffer = (char*) malloc(sizeof(char) * BUFFER_LENGTH);

	copy(&buffer[0], &issueDMAMarker, sizeof(issueDMAMarker));
	copy(&buffer[sizeof(issueDMAMarker)], &ariel_src, sizeof(ariel_src));
	copy(&buffer[sizeof(issueDMAMarker) + sizeof(ariel_src)], &ariel_dest, sizeof(ariel_dest));
	copy(&buffer[sizeof(issueDMAMarker) + sizeof(ariel_src) + sizeof(ariel_dest)],
		&length, sizeof(length));

	write(pipe_id[thr], buffer, BUFFER_LENGTH);

	free(buffer);

#ifdef ARIEL_DEBUG
	printf("Done with ariel memcpy.\n");
#endif

	return 0;
}

void* ariel_tlvl_malloc(size_t size) {
#ifdef ARIEL_DEBUG
	printf("Perform a tlvl_malloc from Ariel %llu\n", size);
#endif
	if(0 == size) {
		printf("YOU REQUESTED ZERO BYTES\n");
		void *bt_entries[64];
		int entry_returned = backtrace(bt_entries, 64);
		backtrace_symbols_fd(bt_entries, entry_returned, 1);
		exit(-8);
	}

	size_t page_diff = (4096 - (size % ((size_t) 4096)));
	size_t real_req_size = size;

	if(page_diff > 0) {
		real_req_size = size + page_diff;
	}

	THREADID currentThread = PIN_ThreadId();
	UINT32 thr = (UINT32) currentThread;

#ifdef ARIEL_DEBUG
	printf("Requested: %llu, but expanded to: %llu (on thread: %lu) \n", size, real_req_size,
		thr);
#endif

	void* real_ptr = 0;
	posix_memalign(&real_ptr, 4096, real_req_size);

	const uint8_t  issueTLMMarker = (uint8_t) ISSUE_TLM_MAP;
	const uint64_t virtualAddress = (uint64_t) real_ptr;
	const uint64_t allocationLength = (uint64_t) real_req_size;

	const int BUFFER_LENGTH = sizeof(issueTLMMarker) +
		sizeof(virtualAddress) + sizeof(allocationLength);
	char* buffer = (char*) malloc(sizeof(char) * BUFFER_LENGTH);

	copy(&buffer[0], &issueTLMMarker, sizeof(issueTLMMarker));
	copy(&buffer[sizeof(issueTLMMarker)], &virtualAddress, sizeof(virtualAddress));
	copy(&buffer[sizeof(issueTLMMarker) + sizeof(virtualAddress)], &allocationLength,
		sizeof(allocationLength));

        write(pipe_id[thr], buffer, BUFFER_LENGTH);

#ifdef ARIEL_DEBUG
	printf("Ariel tlvl_malloc call allocates data at address: %llu\n",
		(uint64_t) real_ptr);
#endif

	free(buffer);

	return real_ptr;
}

void ariel_tlvl_free(void* ptr) {
	THREADID currentThread = PIN_ThreadId();
	UINT32 thr = (UINT32) currentThread;

#ifdef ARIEL_DEBUG
	printf("Perform a tlvl_free from Ariel (pointer = %p) on thread %lu\n", ptr, thr);
#endif
	free(ptr);
	
	const uint8_t issueFree = (uint8_t) ISSUE_TLM_FREE;
	const uint64_t virtAddr = (uint64_t) ptr;
	const int BUFFER_LENGTH = sizeof(issueFree) + sizeof(virtAddr);
	
	char* buffer = (char*) malloc(sizeof(char) * BUFFER_LENGTH);
	copy(&buffer[0], &issueFree, sizeof(issueFree));
	copy(&buffer[sizeof(issueFree)], &virtAddr, sizeof(virtAddr));
	
	write(pipe_id[thr], buffer, BUFFER_LENGTH);	
}

void mapped_ariel_enable() {
	printf("ARIEL: Enabling memory and instruction tracing from program control.\n");
 	enable_output = true;
}

VOID InstrumentRoutine(RTN rtn, VOID* args) {
/*	if(RTN_Name(rtn) == "malloc") {
		// We need to replace with something here
		std::cout << "Identified a malloc replacement function." << std::endl;
	} else if (RTN_Name(rtn) == "tlvl_malloc") {
		// This means malloc far away.
		printf("Identified routine: tlvl_malloc, replacing with Ariel equivalent...\n");
		RTN_Replace(rtn, (AFUNPTR) ariel_tlvl_malloc);
		printf("Replacement complete.\n");
	} else if (RTN_Name(rtn) == "tlvl_free") {
		printf("Identified routine: tlvl_free, replacing with Ariel equivalent...\n");
		RTN_Replace(rtn, (AFUNPTR) ariel_tlvl_free);
		printf("Replacement complete.\n");
	} else*/ if (RTN_Name(rtn) == "ariel_enable") {
		printf("Identified routine: ariel_enable, replacing with Ariel equivalent...\n");
		RTN_Replace(rtn, (AFUNPTR) mapped_ariel_enable);
		printf("Replacement complete.\n");
 	}


 /*else if (RTN_Name(rtn) == "tlvl_memcpy" ) {
	//	printf("Identified routine: tlvl_memcpy, replacing with Ariel equivalent...\n");
	//	RTN_Replace(rtn, (AFUNPTR) ariel_tlvl_memcpy);
	//	printf("Replacement complete.\n");
	}*/
}

/* ===================================================================== */
/* Print Help Message                                                    */
/* ===================================================================== */

INT32 Usage()
{
    PIN_ERROR( "This Pintool collects statistics for instructions.\n" 
              + KNOB_BASE::StringKnobSummary() + "\n");
    return -1;
}

/* ===================================================================== */
/* Main                                                                  */
/* ===================================================================== */

int main(int argc, char *argv[])
{
    if (PIN_Init(argc, argv)) return Usage();

    // Load the symbols ready for us to mangle functions.
    PIN_InitSymbols();
    PIN_AddFiniFunction(Fini, 0);

    if(SSTVerbosity.Value() > 0) {
	std::cout << "SSTARIEL: Loading Ariel Tool to connect to SST on pipe: " <<
		SSTNamedPipe.Value() << " max instruction count: " <<
		MaxInstructions.Value() <<
		" max core count: " << MaxCoreCount.Value() << std::endl;
    }

    core_count = MaxCoreCount.Value();
    pipe_id = (int*) malloc(sizeof(int) * core_count);

    for(int i = 0; i < core_count; ++i) {
	    const char* named_pipe_path = SSTNamedPipe.Value().c_str();
	    char* named_pipe_path_core = (char*) malloc(sizeof(char) * FILENAME_MAX);
	    sprintf(named_pipe_path_core, "%s-%d", named_pipe_path, i);

	    pipe_id[i] = open(named_pipe_path_core, O_WRONLY);

	    if(pipe_id[i] < 0) {
		fprintf(stderr, "ERROR: Unable to connect to pipe: %s from ARIEL\n",
			named_pipe_path_core);
		exit(-1);
    	    } else {
		printf("Successfully created write pipe for: %s\n", named_pipe_path_core);
            }
    }

	printf("ARIEL-SST PIN tool activating with %lu threads\n", core_count);
	fflush(stdout);

    sleep(1);

    if(StartupMode.Value() == 1) {
	printf("ARIEL: Tool is configured to begin with profiling immediately.\n");
	enable_output = true;
    } else if (StartupMode.Value() == 0) {
	printf("ARIEL: Tool is configured to suspend profiling until program control\n");
	enable_output = false;
    }

//    InitLock(&pipe_lock);
    INS_AddInstrumentFunction(InstrumentInstruction, 0);
    RTN_AddInstrumentFunction(InstrumentRoutine, 0);

    PIN_StartProgram();

    return 0;
}

